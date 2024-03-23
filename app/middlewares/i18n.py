import gettext
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
        self.current_locale: str | None = None
        self.translation: gettext.GNUTranslations | None = None

    async def dispatch(self, request: Request, call_next):
        """
        Dispatch the given request through the middleware chain.
        It sets the language for the request based on the `Accept-Language` header.

        :param request: The request being dispatched.
        :param call_next: The next middleware in the chain.
        :return: The response from the next middleware in the chain.
        """
        locale: str | None = request.headers.get("Accept-Language")
        locale = settings.DEFAULT_LOCALE if not locale else locale

        if locale != self.current_locale:
            logger.debug(f"Setting locale to {locale}")
            self.current_locale = locale
            try:
                self.translation = gettext.translation('base', localedir=settings.LOCALE_DIR, languages=[locale])
            except FileNotFoundError:
                logger.debug(f"Locale {locale} not found, setting to default")
                self.translation = gettext.translation('base', localedir=settings.LOCALE_DIR, languages=[settings.DEFAULT_LOCALE])

        request.state.translation = self.translation
        
        response = await call_next(request)
        return response