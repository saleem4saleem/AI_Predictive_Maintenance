from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    asset_component_routes,
    asset_detail_routes,
    assets_routes,
    feedback_routes,
    health_routes,
    maintenance_notification_routes,
    maintenance_plan_routes,
    model_routes,
    notification_proposal_routes,
    overview_routes,
    prediction_routes,
    rag_routes,
    recommendation_routes,
    sensor_routes,
)


api_router = APIRouter()
api_router.include_router(health_routes.router)
api_router.include_router(overview_routes.router)
api_router.include_router(asset_component_routes.router)
api_router.include_router(asset_detail_routes.router)
api_router.include_router(assets_routes.router)
api_router.include_router(sensor_routes.router)
api_router.include_router(prediction_routes.router)
api_router.include_router(maintenance_notification_routes.router)
api_router.include_router(maintenance_plan_routes.router)
api_router.include_router(recommendation_routes.router)
api_router.include_router(rag_routes.router)
api_router.include_router(feedback_routes.router)
api_router.include_router(model_routes.router)
api_router.include_router(notification_proposal_routes.router)
