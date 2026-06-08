from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from app.core.config import get_settings

try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
except ImportError:
    text = None
    async_sessionmaker = None
    create_async_engine = None


settings = get_settings()


def _create_engine() -> Any | None:
    if create_async_engine is None or settings.async_database_url is None:
        return None

    return create_async_engine(
        settings.async_database_url,
        pool_pre_ping=True,
        future=True,
    )


async_engine = _create_engine()
AsyncSessionLocal = (
    async_sessionmaker(async_engine, expire_on_commit=False)
    if async_engine is not None and async_sessionmaker is not None
    else None
)


async def get_db_session() -> AsyncIterator[Any]:
    if AsyncSessionLocal is None:
        raise RuntimeError("Database session requested before database is configured.")

    async with AsyncSessionLocal() as session:
        yield session


async def check_database_connection() -> dict[str, Any]:
    if settings.database_url is None:
        return {
            "component": "database",
            "ok": False,
            "status": "not_configured",
            "detail": "DATABASE_URL is not configured.",
        }

    if create_async_engine is None or text is None:
        return {
            "component": "database",
            "ok": False,
            "status": "unavailable",
            "detail": "SQLAlchemy is not installed in the current environment.",
        }

    if async_engine is None:
        return {
            "component": "database",
            "ok": False,
            "status": "unavailable",
            "detail": "Database engine could not be initialized.",
        }

    try:
        async with async_engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        return {
            "component": "database",
            "ok": False,
            "status": "unavailable",
            "detail": exc.__class__.__name__,
        }

    return {
        "component": "database",
        "ok": True,
        "status": "healthy",
        "detail": "Database connection succeeded.",
    }


async def dispose_database_engine() -> None:
    if async_engine is not None:
        await async_engine.dispose()
