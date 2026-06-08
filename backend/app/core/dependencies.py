from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.database import get_db_session


def get_app_settings() -> Settings:
    return get_settings()


SettingsDependency = Annotated[Settings, Depends(get_app_settings)]
DatabaseSessionDependency = Annotated[Any, Depends(get_db_session)]
