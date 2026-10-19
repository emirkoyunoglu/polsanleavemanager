"""RFC 9457 problem+json responses — the one error pattern (docs/conventions.md, Error handling).

User-facing text is Turkish; stack traces, SQL, paths and exception messages never leave the
server: unexpected errors are logged with a correlation id that the response carries.
"""

import logging
import uuid
from collections.abc import Mapping
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.errors import DomainError

PROBLEM_JSON = "application/problem+json"

logger = logging.getLogger("app")

_HTTP_TEXTS: dict[int, tuple[str, str]] = {
    404: ("Bulunamadı", "İstenen adres bulunamadı."),
    405: ("Yönteme izin verilmiyor", "Bu adres bu istek yöntemini desteklemiyor."),
}


def problem(
    status: int,
    title: str,
    detail: str,
    *,
    headers: Mapping[str, str] | None = None,
    **extra: Any,
) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail, **extra}
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON, headers=headers)


def install_problem_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(DomainError, _domain_error)
    app.add_exception_handler(Exception, _unexpected_error)


# Starlette registers handlers per exception class, so `exc` is always that class; the cast
# only narrows the generic handler signature for the type checker.
async def _http_error(_request: Request, exc: Exception) -> Response:
    error = cast(StarletteHTTPException, exc)
    title, detail = _HTTP_TEXTS.get(
        error.status_code, ("İstek işlenemedi", "İstek işlenirken bir sorun oluştu.")
    )
    # Protocol headers (405 Allow, 401 WWW-Authenticate) must survive the rewrite.
    return problem(error.status_code, title, detail, headers=error.headers)


async def _validation_error(_request: Request, exc: Exception) -> Response:
    error = cast(RequestValidationError, exc)
    fields = [".".join(str(part) for part in item["loc"]) for item in error.errors()]
    return problem(422, "Geçersiz istek", "İstekteki bazı alanlar geçersiz.", fields=fields)


async def _domain_error(_request: Request, exc: Exception) -> Response:
    error = cast(DomainError, exc)
    return problem(error.status, error.title, error.detail)


async def _unexpected_error(_request: Request, exc: Exception) -> Response:
    correlation_id = uuid.uuid4().hex
    logger.error("unhandled error [%s]", correlation_id, exc_info=exc)
    return problem(
        500,
        "Beklenmeyen hata",
        "Beklenmeyen bir hata oluştu. Sorun sürerse bu kodu destek ekibine iletin.",
        correlation_id=correlation_id,
    )
