import decouple

from src.config.settings.base import Settings
from src.config.settings.environment import Environment


class DevelopmentSettings(Settings):
    DESCRIPTION: str | None = (
        "Development Settings -- Backend application with FastAPI, PostgreSQL via SQLAlchemy with Alembic, and Docker."
    )
    DEBUG: bool = True
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # CLIENT_CERT_PATH: str = decouple.config("CLIENT_CERT_PATH", cast=str)  # type: ignore
    # CLIENT_KEY_PATH: str = decouple.config("CLIENT_KEY_PATH", cast=str)  # type: ignore
    # SERVER_CA_PATH: str = decouple.config("SERVER_CA_PATH", cast=str)  # type: ignore
