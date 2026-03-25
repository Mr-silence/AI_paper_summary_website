import json
import subprocess
import sys
import time
from pathlib import Path

import pymysql

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts._common import (
    MYSQLADMIN_BIN,
    MYSQLD_BIN,
    MYSQL_BASE_DIR,
    MYSQL_DATA_DIR,
    MYSQL_SERVER_SCRIPT,
    detect_existing_socket,
    is_tcp_open,
    parse_database_url,
)


SYSTEM_MYSQL_USER = "_mysql"
ENV_PATH = PROJECT_ROOT / ".env"


def _data_dir_initialized() -> bool:
    if not MYSQL_DATA_DIR.exists():
        return False
    if (MYSQL_DATA_DIR / "mysql").exists():
        return True
    return any(MYSQL_DATA_DIR.iterdir())


def _run_command(
    command: list[str],
    *,
    use_sudo: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    final_command = command
    if use_sudo:
        final_command = ["sudo", "-n", *command]

    return subprocess.run(
        final_command,
        check=check,
        text=True,
        capture_output=True,
    )


def _connect_mysql(password: str | None, socket_path: str | None = None):
    parsed = parse_database_url()
    kwargs = {
        "user": parsed.username or "root",
        "charset": "utf8mb4",
        "autocommit": True,
    }
    if password is not None:
        kwargs["password"] = password
    if socket_path:
        kwargs["unix_socket"] = socket_path
    else:
        kwargs["host"] = parsed.host or "localhost"
        kwargs["port"] = int(parsed.port or 3306)
    return pymysql.connect(**kwargs)


def _configured_connection_works(socket_path: str | None = None) -> bool:
    parsed = parse_database_url()
    try:
        with _connect_mysql(parsed.password or "", socket_path=socket_path):
            return True
    except Exception:
        return False


def _ensure_installation() -> None:
    required_paths = [
        MYSQL_BASE_DIR,
        MYSQLD_BIN,
        MYSQLADMIN_BIN,
        MYSQL_SERVER_SCRIPT,
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"System MySQL installation is incomplete: {missing}")


def _ensure_data_dir_exists() -> None:
    if MYSQL_DATA_DIR.exists():
        return
    _run_command(["/bin/mkdir", "-p", str(MYSQL_DATA_DIR)], use_sudo=True)


def _ensure_data_dir_permissions() -> None:
    _run_command(["/usr/sbin/chown", "-R", SYSTEM_MYSQL_USER, str(MYSQL_DATA_DIR)], use_sudo=True)


def _initialize_data_dir() -> None:
    _ensure_data_dir_exists()
    _ensure_data_dir_permissions()
    _run_command(
        [
            str(MYSQLD_BIN),
            "--initialize-insecure",
            f"--user={SYSTEM_MYSQL_USER}",
            f"--basedir={MYSQL_BASE_DIR}",
            f"--datadir={MYSQL_DATA_DIR}",
        ],
        use_sudo=True,
    )
    _ensure_data_dir_permissions()


def _wait_for_tcp_ready(timeout_seconds: int = 60) -> None:
    parsed = parse_database_url()
    host = parsed.host or "localhost"
    port = int(parsed.port or 3306)
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if is_tcp_open(host, port):
            return
        time.sleep(1)
    raise TimeoutError(f"MySQL TCP endpoint {host}:{port} did not become ready within {timeout_seconds} seconds.")


def _start_system_mysql() -> None:
    parsed = parse_database_url()
    if is_tcp_open(parsed.host or "localhost", int(parsed.port or 3306)):
        return

    result = _run_command([str(MYSQL_SERVER_SCRIPT), "start"], use_sudo=True, check=False)
    if result.returncode != 0 and not is_tcp_open(parsed.host or "localhost", int(parsed.port or 3306)):
        stderr = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"mysql.server start failed: {stderr or 'unknown error'}")

    _wait_for_tcp_ready()


def _bootstrap_root_password() -> None:
    parsed = parse_database_url()
    username = parsed.username or "root"
    password = parsed.password or ""

    if username != "root":
        raise RuntimeError("Initial system MySQL bootstrap requires DATABASE_URL to use the root account.")

    if not password:
        return

    socket_path = detect_existing_socket()
    try:
        with _connect_mysql(password="", socket_path=socket_path) as connection:
            with connection.cursor() as cursor:
                cursor.execute("ALTER USER 'root'@'localhost' IDENTIFIED BY %s", (password,))
                cursor.execute("FLUSH PRIVILEGES")
    except Exception as exc:
        raise RuntimeError(
            "System MySQL started, but the root account could not be bootstrapped to the password from DATABASE_URL."
        ) from exc


def _mysqladmin_ping() -> None:
    parsed = parse_database_url()
    command = [
        str(MYSQLADMIN_BIN),
        "--protocol=tcp",
        "-h",
        parsed.host or "localhost",
        "-P",
        str(int(parsed.port or 3306)),
        "-u",
        parsed.username or "root",
    ]
    if parsed.password:
        command.append(f"-p{parsed.password}")
    command.append("ping")
    _run_command(command)


def _clear_socket_override() -> None:
    if not ENV_PATH.exists():
        return

    lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    updated = False
    for index, line in enumerate(lines):
        if line.startswith("MYSQL_UNIX_SOCKET="):
            lines[index] = 'MYSQL_UNIX_SOCKET=""'
            updated = True
            break
    if not updated:
        lines.append('MYSQL_UNIX_SOCKET=""')
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_mysql_server_ready() -> dict[str, object]:
    _ensure_installation()
    parsed = parse_database_url()
    initialized_now = False

    if _configured_connection_works():
        _mysqladmin_ping()
        _clear_socket_override()
        return {
            "mysql_ready": True,
            "connection_mode": "tcp",
            "host": parsed.host or "localhost",
            "port": int(parsed.port or 3306),
            "socket": None,
            "initialized_now": False,
            "data_dir": str(MYSQL_DATA_DIR),
        }

    if not _data_dir_initialized():
        _initialize_data_dir()
        initialized_now = True

    _start_system_mysql()

    if initialized_now and not _configured_connection_works():
        _bootstrap_root_password()

    if not _configured_connection_works():
        raise RuntimeError(
            "System MySQL is running, but DATABASE_URL credentials still cannot authenticate over TCP."
        )

    _mysqladmin_ping()
    _clear_socket_override()
    return {
        "mysql_ready": True,
        "connection_mode": "tcp",
        "host": parsed.host or "localhost",
        "port": int(parsed.port or 3306),
        "socket": None,
        "initialized_now": initialized_now,
        "data_dir": str(MYSQL_DATA_DIR),
    }


def main() -> None:
    result = ensure_mysql_server_ready()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
