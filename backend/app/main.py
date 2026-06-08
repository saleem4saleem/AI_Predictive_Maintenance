from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.contracts.base_response_contract import DataResponseContract
from app.core.config import get_settings
from app.core.database import dispose_database_engine
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await dispose_database_engine()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", response_model=DataResponseContract, tags=["root"])
    async def root() -> DataResponseContract:
        return DataResponseContract(
            message="Predictive maintenance API is running.",
            data={
                "project": settings.project_name,
                "api_version": "v1",
                "health_url": f"{settings.api_v1_prefix}/health",
            },
        )

    return app


app = create_app()
