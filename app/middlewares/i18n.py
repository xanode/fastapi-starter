import gettext
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings, SupportedLocales


logger = logging.getLogger("app.middleware.i18n")


def parse_accept_language_header(accept_language: str) -> SupportedLocales:
    """
    Parse the `Accept-Language` header and return the supported locales in order of preference.
    The `Accept-Language` is described by the following ABNF:
        Accept-Language  = #( language-range [ weight ] )                       ; [RFC9110]
        language-range   = (1*8ALPHA *("-" 1*8alphanum)) / "*"                  ; [RFC4647]
        alphanum         = ALPHA / DIGIT                                        ; [RFC4647]
        weight           = OWS ";" OWS "q=" qvalue                              ; [RFC9110]
        qvalue           = ( "0" [ "." 0*3DIGIT ] ) / ( "1" [ "." 0*3("0") ] )  ; [RFC9110]
    
    We choose not to implement the full ABNF, but rather a simplified version that works for most cases.
    The function returns the supported locale in order of preference. If no supported locale is found, it returns the default locale.

    :param accept_language: The `Accept-Language` header.
    :return: The supported locales in order of preference.
    """
    # Split the header by `,` and strip the whitespace
    languages = accept_language.split(",")
    # Split the language by `;` and strip the whitespace
    languages = [language.split(";") for language in languages]
    # Extract the language and weight
    languages = [(language[0].strip(), float(language[1].split("=")[1].strip()) if len(language) > 1 else 1.0) for language in languages]

    # Sort the languages by weight in descending order
    languages.sort(key=lambda x: x[1], reverse=True)

    # Extract the language from the sorted list
    languages = [language[0] for language in languages]

    # Check if the language is supported
    for language in languages:
        if language in settings.SUPPORTED_LOCALES:
            return language
        else:
            # Check if the language is a prefix of the supported locales
            for locale in settings.SUPPORTED_LOCALES:
                if locale.startswith(language):
                    return locale

    return settings.DEFAULT_LOCALE


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
        locale = settings.DEFAULT_LOCALE if not locale else parse_accept_language_header(locale)

        if locale != self.current_locale:
            logger.debug(f"Setting locale to {locale}")
            self.current_locale = locale
            try:
                self.translation = gettext.translation('base', localedir=settings.LOCALE_DIR, languages=[locale])
            except FileNotFoundError:
                logger.warning(f"Locale {locale} not found, but should be supported. Setting to default")
                self.translation = gettext.translation('base', localedir=settings.LOCALE_DIR, languages=[settings.DEFAULT_LOCALE])

        request.state.translation = self.translation
        
        response = await call_next(request)
        return response