import socket
import sys
import time
from pathlib import Path

from sqlalchemy.engine import URL, make_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings  # noqa: E402


MYSQL_BASE_DIR = Path("/usr/local/mysql")
MYSQL_DATA_DIR = MYSQL_BASE_DIR / "data"
MYSQLD_BIN = MYSQL_BASE_DIR / "bin" / "mysqld"
MYSQLD_SAFE_BIN = MYSQL_BASE_DIR / "bin" / "mysqld_safe"
MYSQL_CLIENT_BIN = MYSQL_BASE_DIR / "bin" / "mysql"
MYSQLADMIN_BIN = MYSQL_BASE_DIR / "bin" / "mysqladmin"
MYSQL_SERVER_SCRIPT = MYSQL_BASE_DIR / "support-files" / "mysql.server"


def parse_database_url() -> URL:
    return make_url(settings.DATABASE_URL)


def mysql_socket_candidates() -> list[str]:
    candidates: list[str] = []
    if settings.MYSQL_UNIX_SOCKET.strip():
        candidates.append(settings.MYSQL_UNIX_SOCKET.strip())
    candidates.extend(
        [
            "/tmp/mysql.sock",
            "/var/run/mysqld/mysqld.sock",
            "/opt/homebrew/var/mysql/mysql.sock",
        ]
    )

    deduped: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in deduped:
            deduped.append(candidate)
    return deduped


def detect_existing_socket() -> str | None:
    for candidate in mysql_socket_candidates():
        if Path(candidate).exists():
            return candidate
    return None


def is_tcp_open(host: str, port: int, timeout_seconds: float = 1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout_seconds)
        return sock.connect_ex((host, port)) == 0


def wait_for_mysql(host: str, port: int, timeout_seconds: int = 60) -> dict[str, str | int | None]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if is_tcp_open(host, port):
            return {"mode": "tcp", "host": host, "port": port, "socket": None}

        socket_path = detect_existing_socket()
        if socket_path:
            return {"mode": "socket", "host": host, "port": port, "socket": socket_path}

        time.sleep(1)

    raise TimeoutError(f"MySQL did not become ready within {timeout_seconds} seconds.")
