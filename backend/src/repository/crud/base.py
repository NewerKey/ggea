from sqlalchemy.ext.asyncio import (
    async_sessionmaker as sqlalchemy_async_sessionmaker,
    AsyncSession as SQLAlchemyAsyncSession,
)
from sqlalchemy.pool import PoolProxiedConnection as SQLAlchemyProxiedConnection


class BaseCRUDRepository:
    def __init__(self, async_session: sqlalchemy_async_sessionmaker[SQLAlchemyAsyncSession]):
        self.async_session = async_session()
