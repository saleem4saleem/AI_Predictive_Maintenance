from __future__ import annotations

from pydantic import BaseModel, Field

from app.contracts.asset_component_contract import (
    AssetComponent,
    ComponentMaintenanceHistory,
    ComponentUpcomingTask,
)
from app.contracts.asset_contract import AssetBasicResponse
from app.contracts.maintenance_plan_contract import MaintenancePlanResponse
from app.contracts.prediction_contract import PredictionResponse
from app.contracts.rag_contract import RagSearchResult
from app.contracts.recommendation_contract import RecommendationItem


class CurrentConditionContract(BaseModel):
    health_score: float
    condition: str
    trend: str | None = None
    last_updated: str | None = None


class SensorSummaryContract(BaseModel):
    timestamp: str | None = None
    vibration: float | None = None
    temperature: float | None = None
    pressure: float | None = None
    current_value: float | None = None
    speed: float | None = None
    flow: float | None = None


class RecommendedActionContract(RecommendationItem):
    pass


class SimilarFailureContract(RagSearchResult):
    pass


class AIExplanationContract(BaseModel):
    summary: str
    confidence: str
    fallback_used: bool = False


class FeedbackStatusContract(BaseModel):
    feedback_required: bool
    last_feedback_at: str | None = None


class AssetDetailResponse(BaseModel):
    asset: AssetBasicResponse
    current_condition: CurrentConditionContract
    sensor_summary: SensorSummaryContract
    prediction: PredictionResponse
    maintenance_plan: MaintenancePlanResponse
    recommended_actions: list[RecommendedActionContract]
    similar_failures: list[SimilarFailureContract]
    ai_explanation: AIExplanationContract
    feedback_status: FeedbackStatusContract
    components: list[AssetComponent] = Field(default_factory=list)
    asset_maintenance_history: list[ComponentMaintenanceHistory] = Field(default_factory=list)
    asset_upcoming_tasks: list[ComponentUpcomingTask] = Field(default_factory=list)


AssetDetailContract = AssetDetailResponse
