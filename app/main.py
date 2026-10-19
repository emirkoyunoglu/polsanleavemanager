"""Application factory. Run locally: python -m uvicorn app.main:create_app --factory"""

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.calendar.api import DEFAULT_DATA_DIR, init_calendar
from app.shared.db import create_db_engine, is_reachable, run_migrations
from app.shared.problem import install_problem_handlers, problem
from app.shared.settings import Settings

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

# The complete unauthenticated surface (spec 0001 R-2): exact paths plus path prefixes (the home
# page's static assets). Everything else is default-deny (docs/security.md); the authentication
# guard (F4) uses these as its allowlist. A test pins every route to this list.
PUBLIC_PATHS = frozenset({"/", "/api/health"})
PUBLIC_PATH_PREFIXES = ("/static/",)

# docs/security.md, Input & output: same-origin resources only, no inline script; no MIME sniffing.
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
}


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

    @app.middleware("http")
    async def security_headers(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        return response

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html", media_type="text/html; charset=utf-8")

    @app.get("/api/health")
    def health(request: Request) -> JSONResponse:
        if not is_reachable(request.app.state.engine):
            return problem(503, "Hizmet hazır değil", "Veritabanına erişilemiyor.")
        return JSONResponse({"status": "ok"})

    return app
