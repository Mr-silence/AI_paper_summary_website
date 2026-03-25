import subprocess
from pathlib import Path

import pytest

from tests.conftest import FRONTEND_DIR


pytestmark = pytest.mark.smoke


def test_frontend_build_smoke(tmp_path):
    out_dir = tmp_path / "frontend-build"
    result = subprocess.run(
        ["npm", "run", "build", "--", "--outDir", str(out_dir)],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert out_dir.exists()
