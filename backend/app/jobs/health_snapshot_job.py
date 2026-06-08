from app.services.overview_service import get_overview


def build_health_snapshot() -> dict:
    overview = get_overview()
    return overview.model_dump()
