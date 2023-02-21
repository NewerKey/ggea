from src.config.setup import settings
from src.security.authentication.api_key import CustomAPIKeyCookie, CustomAPIKeyHeader, CustomAPIKeyQuery
from src.utility.typing.api_key import CustomAPIKey


class APIKeyFactory:
    @staticmethod
    def initialize_api_key(method: str, is_auto_error: bool) -> CustomAPIKey:
        if method == "ce":
            return CustomAPIKeyCookie(name=settings.API_COOKIE_SECRET_KEY, auto_error=is_auto_error)
        elif method == "hr":
            return CustomAPIKeyHeader(name=settings.API_HEADER_SECRET_KEY, auto_error=is_auto_error)
        elif method == "qy":
            return CustomAPIKeyQuery(name=settings.API_QUERY_SECRET_KEY, auto_error=is_auto_error)
        raise Exception("The method for the listed custom API Key is invalid!")


def get_api_key(method: str, is_auto_error: bool = True) -> CustomAPIKey:
    return APIKeyFactory.initialize_api_key(method=method, is_auto_error=is_auto_error)
