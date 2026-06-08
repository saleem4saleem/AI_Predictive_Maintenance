from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.contracts.base_response_contract import BaseResponseContract
from app.core.config import Settings, get_settings
from app.core.database import check_database_connection
from app.services.model_monitoring_service import get_active_model_status


router = APIRouter(prefix="/health", tags=["health"])


class HealthResponseContract(BaseResponseContract):
    data: dict[str, Any] = Field(default_factory=dict)


def _backend_health(settings: Settings) -> dict[str, Any]:
    return {
        "component": "backend",
        "ok": True,
        "status": "healthy",
        "detail": "FastAPI application is running.",
        "environment": settings.environment,
        "api_prefix": settings.api_v1_prefix,
    }


def _model_health(settings: Settings) -> dict[str, Any]:
    return get_active_model_status()


def _overall_status(components: list[dict[str, Any]]) -> str:
    return "healthy" if all(component["ok"] for component in components) else "degraded"


@router.get("", response_model=HealthResponseContract)
async def get_health() -> HealthResponseContract:
    settings = get_settings()
    components = [
        _backend_health(settings),
        await check_database_connection(),
        _model_health(settings),
    ]

    return HealthResponseContract(
        message="Health checks completed.",
        data={
            "status": _overall_status(components),
            "components": components,
        },
    )


@router.get("/backend", response_model=HealthResponseContract)
async def get_backend_health() -> HealthResponseContract:
    settings = get_settings()
    return HealthResponseContract(
        message="Backend health check completed.",
        data=_backend_health(settings),
    )


@router.get("/database", response_model=HealthResponseContract)
async def get_database_health() -> HealthResponseContract:
    return HealthResponseContract(
        message="Database health check completed.",
        data=await check_database_connection(),
    )


@router.get("/model", response_model=HealthResponseContract)
async def get_model_health() -> HealthResponseContract:
    settings = get_settings()
    return HealthResponseContract(
        message="Model health check completed.",
        data=_model_health(settings),
    )
