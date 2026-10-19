"""Application factory. Run locally: python -m uvicorn app.main:create_app --factory"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.calendar.api import DEFAULT_DATA_DIR, init_calendar
from app.shared.db import create_db_engine, is_reachable, run_migrations
from app.shared.problem import install_problem_handlers, problem
from app.shared.settings import Settings

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

# The only routes reachable without authentication (spec 0001 R-2). Everything added later is
# default-deny (docs/security.md); the authentication guard (F4) treats this set as the allowlist.
PUBLIC_PATHS = frozenset({"/", "/api/health"})


def create_app(
    settings: Settings | None = None, holiday_data_dir: Path = DEFAULT_DATA_DIR
) -> FastAPI:
    resolved = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        init_calendar(holiday_data_dir)  # invalid holiday data stops startup (R-12)
        run_migrations(resolved.database_url)
        app.state.engine = create_db_engine(resolved.database_url)
        try:
            yield
        finally:
            app.state.engine.dispose()

    # Interactive API docs and the OpenAPI schema stay off: they would be unauthenticated routes.
    app = FastAPI(
        title="Polsan İzin Yönetimi",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    install_problem_handlers(app)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")

    @app.get("/api/health")
    def health(request: Request) -> JSONResponse:
        if not is_reachable(request.app.state.engine):
            return problem(503, "Hizmet hazır değil", "Veritabanına erişilemiyor.")
        return JSONResponse({"status": "ok"})

    return app
