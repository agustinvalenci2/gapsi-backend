import pytest
from app.core.config import get_settings
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "database_url", "sqlite://:memory:")
    monkeypatch.setattr(settings, "generate_schemas", True)
    with TestClient(app) as test_client:
        yield test_client
