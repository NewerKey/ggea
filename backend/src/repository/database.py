import ssl
from functools import lru_cache

import loguru
import pydantic
from sqlalchemy.ext.asyncio import (
    async_sessionmaker as sqlalchemy_async_sessionmaker,
    AsyncEngine as SQLAlchemyAsyncEngine,
    AsyncSession as SQLAlchemyAsyncSession,
    create_async_engine as create_sqlalchemy_async_engine,
)
from sqlalchemy.pool import QueuePool as SQLAlchemyQueuePool

from src.config.setup import settings


class Database:
    """
    Database for:
        - Asyncrhonous SQLAlchemy.
        - Asynchronous Postgres Server
    """

    def __init__(self):
        self.server: str = "Asynchronous Postgres"
        self.framework: str = "Asynchronous SQLAlchemy"
        self.is_async: bool = settings.IS_DB_ASYNC_DRIVER
        self._async_engine: SQLAlchemyAsyncEngine | None = None
        self._async_session: sqlalchemy_async_sessionmaker[SQLAlchemyAsyncSession] | None = None
        self.postgres_uri: pydantic.PostgresDsn = pydantic.PostgresDsn(
            url=f"{settings.DB_POSTGRES_SCHEMA}://{settings.DB_POSTGRES_USERNAME}:{settings.DB_POSTGRES_PASSWORD}@{settings.DB_POSTGRES_HOST}:{settings.DB_POSTGRES_PORT}/{settings.DB_POSTGRES_NAME}",
            scheme=settings.DB_POSTGRES_SCHEMA,
        )
        self._ssl_context: ssl.SSLContext | None = None

    @property
    def set_async_driver(self) -> pydantic.PostgresDsn | str:
        return (
            self.postgres_uri.replace("postgresql://", "postgresql+asyncpg://") if self.is_async else self.postgres_uri
        )

    @property
    def ssl_context(self):
        if self._ssl_context:
            return self._ssl_context
        else:
            self.initialize_ssl_context
        return self.ssl_context

    @property
    def initialize_ssl_context(self) -> None:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_ctx.load_cert_chain(certfile=settings.CLIENT_CERT_PATH, keyfile=settings.CLIENT_KEY_PATH)
        ssl_ctx.load_verify_locations(cafile=settings.SERVER_CA_PATH)
        self._ssl_context = ssl_ctx

    @property
    def async_engine(self) -> SQLAlchemyAsyncEngine:
        if self._async_engine:
            return self._async_engine
        else:
            self.initialize_async_engine
        return self.async_engine

    @property
    def initialize_async_engine(self) -> None:
        ssl_context = self.ssl_context if settings.ENVIRONMENT == "PROD" else None

        self._async_engine = create_sqlalchemy_async_engine(
            url=self.set_async_driver,
            echo=settings.IS_DB_ECHO_LOG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_POOL_OVERFLOW,
            poolclass=SQLAlchemyQueuePool,
            connect_args={"ssl": ssl_context},
        )

    @property
    def async_session(self) -> sqlalchemy_async_sessionmaker[SQLAlchemyAsyncSession]:
        if self._async_session:
            return self._async_session
        else:
            self.initialize_async_session
        return self.async_session

    @property
    def initialize_async_session(self) -> None:
        self._async_session = sqlalchemy_async_sessionmaker(bind=self.async_engine, expire_on_commit=False)

    def __call__(self):
        loguru.logger.info(f"SQLAchemy Asynchronous Engine --- Establishing . . .")
        while not self.async_engine:
            loguru.logger.info(f"SQLAchemy Asynchronous Engine --- Not Found! Reinitializing . . .")
            self.initialize_async_engine
        loguru.logger.info(f"SQLAchemy Asynchronous Engine --- Established!")

        loguru.logger.info(f"SQLAchemy Asynchronous Session --- Establishing . . .")
        while not self.async_session:
            loguru.logger.info(f"SQLAchemy Asynchronous Session --- Not Found! Reinitializing . . .")
            self.initialize_async_session
        loguru.logger.info(f"SQLAchemy Asynchronous Session --- Established!")
        return self

    def __str__(self) -> str:
        return f"Database Server: {self.server}\nDatabase Framework: {self.framework}"


def get_database() -> Database:
    return Database()


db = get_database()
