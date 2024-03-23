import logging

from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


logger = logging.getLogger("app.core.exception_handlers")


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Handle IntegrityError exceptions.
    """
    logger.error(f'IntegrityError: {exc}')
    
    _: Callable[[str], str] = request.state.translation.gettext
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": _("INTEGRITY_ERROR")},
    )