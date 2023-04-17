import decouple

from src.config.settings.base import Settings
from src.config.settings.environment import Environment


class ProductionSettings(Settings):
    DESCRIPTION: str | None = (
        "Production Settings -- Backend application with FastAPI, PostgreSQL via SQLAlchemy with Alembic, and Docker."
    )
    DEBUG: bool = True
    ENVIRONMENT: Environment = Environment.PRODUCTION

    DB_POSTGRES_HOST: str = decouple.config("POSTGRES_PROD_HOST", cast=str)  # type: ignore
    DB_POSTGRES_PORT: int = decouple.config("POSTGRES_PROD_PORT", cast=int)  # type: ignore
    DB_POSTGRES_USERNAME: str = decouple.config("POSTGRES_PROD_USERNAME", cast=str)  # type: ignore
    DB_POSTGRES_PASSWORD: str = decouple.config("POSTGRES_PROD_PASSWORD", cast=str)  # type: ignore
    DB_POSTGRES_SCHEMA: str = decouple.config("POSTGRES_PROD_SCHEMA", cast=str)  # type: ignore
    DB_POSTGRES_NAME: str = decouple.config("POSTGRES_PROD_DB", cast=str)  # type: ignore

    CLIENT_CERT_PATH: str = decouple.config("CLIENT_CERT_PATH", cast=str)  # type: ignore
    CLIENT_KEY_PATH: str = decouple.config("CLIENT_KEY_PATH", cast=str)  # type: ignore
    SERVER_CA_PATH: str = decouple.config("SERVER_CA_PATH", cast=str)  # type: ignore
