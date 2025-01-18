from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


database_url = URL.create(
    drivername=settings.db_engine,
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

async_engine = create_async_engine(database_url, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False, autocommit=False
)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
