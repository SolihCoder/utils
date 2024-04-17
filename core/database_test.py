from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import pytest
from core import Base

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def override_get_async_session() -> AsyncSession:
    await create_tables()
    async with async_session() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def cleanup_database():
    await create_tables()

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


__all__ = ['override_get_async_session', 'create_tables']
