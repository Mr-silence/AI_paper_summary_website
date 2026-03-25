import pytest

from app.main import app


pytestmark = pytest.mark.smoke


def test_backend_import_smoke():
    assert app.title == "AI Paper Summary API"
