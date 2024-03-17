import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


logger = logging.getLogger("app.middleware.i18n")


class I18nMiddleware(BaseHTTPMiddleware):
    """
    This middleware is used to set the language for the request based on the
    `Accept-Language` header.
    """
    def __init__(self, app):
        """
        Initialize the middleware with the given FastAPI app.

        :param app: The FastAPI app to which the middleware is being added.
        """
        super().__init__(app)
        self.language: str | None = None

    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the given request through the middleware chain.
        It sets the language for the request based on the `Accept-Language` header.

        :param request: The request being dispatched.
        :param call_next: The next middleware in the chain.
        :return: The response from the next middleware in the chain.
        """
        accept_language = request.headers.get("Accept-Language")
        
        if self.language is None:
            if accept_language is None:
                self.language = settings.LOCALE
            else:
                logger.debug(f"Accept-Language: {accept_language}")
                self.language = accept_language.split(",")[0].strip().split(";")[0]
        
        request.state.language = self.language
        response = await call_next(request)
        return response