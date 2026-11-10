from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.calendar.api as calendar_api
from app.main import create_app
from app.shared.settings import Settings


@pytest.fixture(autouse=True)
def _isolated_calendar(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test starts without a loaded calendar; monkeypatch restores the global afterwards."""
    monkeypatch.setattr(calendar_api, "_calendar", None)


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    return f"sqlite:///{(tmp_path / 'app.db').as_posix()}"


@pytest.fixture
def client(database_url: str) -> Iterator[TestClient]:
    app = create_app(Settings(database_url=database_url))
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
