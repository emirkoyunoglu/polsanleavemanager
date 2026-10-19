"""Application skeleton — spec 0001 AC-1..AC-4, AC-19 (startup)."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.calendar.api import InvalidHolidayData
from app.main import create_app
from app.shared.settings import Settings

pytestmark = pytest.mark.integration

PROBLEM_JSON = "application/problem+json"


def test_health_ok_without_auth(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_503_when_db_unreachable(client: TestClient, tmp_path: Path) -> None:
    # A directory is not a database file: every connection attempt fails.
    client.app.state.engine = create_engine(f"sqlite:///{tmp_path.as_posix()}")  # type: ignore[attr-defined]
    response = client.get("/api/health")
    assert response.status_code == 503
    assert response.headers["content-type"] == PROBLEM_JSON
    assert response.json()["title"] == "Hizmet hazır değil"


def test_home_page_is_turkish_html_with_title_and_h1(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert re.search(r'<html[^>]*\blang="tr"', html)
    assert "<title>Polsan İzin Yönetimi</title>" in html
    assert re.search(r"<h1>\s*Polsan İzin Yönetimi\s*</h1>", html)


def test_unknown_path_returns_turkish_problem_json_404(client: TestClient) -> None:
    response = client.get("/olmayan-adres")
    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert body["status"] == 404
    assert body["title"] == "Bulunamadı"
    assert body["detail"] == "İstenen adres bulunamadı."


def test_method_not_allowed_keeps_allow_header(client: TestClient) -> None:
    response = client.post("/api/health")
    assert response.status_code == 405
    assert response.headers["content-type"] == PROBLEM_JSON
    assert response.headers["allow"] == "GET"
    assert response.json()["title"] == "Yönteme izin verilmiyor"


def test_unhandled_error_returns_generic_500_without_internals(database_url: str) -> None:
    app = create_app(Settings(database_url=database_url))

    def boom() -> None:
        raise RuntimeError(r"secret C:\internal\path.py SELECT * FROM users")

    app.add_api_route("/api/boom", boom)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/boom")

    assert response.status_code == 500
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert body["title"] == "Beklenmeyen hata"
    assert re.fullmatch(r"[0-9a-f]{32}", body["correlation_id"])
    for leaked in ("secret", "internal", "SELECT", "RuntimeError", "Traceback", ".py"):
        assert leaked not in response.text


@pytest.mark.parametrize("path", ["/", "/api/health", "/static/css/main.css", "/olmayan-adres"])
def test_security_headers_on_every_response(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.headers["content-security-policy"] == "default-src 'self'"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_startup_fails_on_invalid_holiday_data(database_url: str, tmp_path: Path) -> None:
    data_dir = tmp_path / "holidays"
    data_dir.mkdir()
    (data_dir / "2026.toml").write_text(
        'year = 2026\n[[holiday]]\ndate = 2026-10-29\nname = "X"\nkind = "evening"\n',
        encoding="utf-8",
    )
    app = create_app(Settings(database_url=database_url), holiday_data_dir=data_dir)
    with pytest.raises(InvalidHolidayData), TestClient(app):
        pass
