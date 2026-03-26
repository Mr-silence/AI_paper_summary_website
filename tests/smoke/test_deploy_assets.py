from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.smoke


def test_linux_deploy_assets_exist():
    assert (PROJECT_ROOT / "deploy" / "linux" / "ai-paper-summary.nginx.conf").exists()
    assert (PROJECT_ROOT / "deploy" / "linux" / "ai-paper-summary-backend.service").exists()
    assert (PROJECT_ROOT / "deploy" / "linux" / "DEPLOY.md").exists()


def test_frontend_production_env_uses_same_origin_api():
    env_path = PROJECT_ROOT / "frontend" / ".env.production"
    content = env_path.read_text(encoding="utf-8")
    assert "VITE_API_BASE_URL=/api" in content
