from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


def _load_dotenv_file(path: Path) -> None:
    """Load simple KEY=VALUE entries without requiring python-dotenv."""

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _load_local_env_files() -> None:
    _load_dotenv_file(PROJECT_ROOT / ".env")
    _load_dotenv_file(BACKEND_DIR / ".env")


_load_local_env_files()


def _get_bool_env(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _get_csv_env(name: str, default: list[str]) -> list[str]:
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _get_first_env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        raw_value = os.getenv(name)
        if raw_value not in {None, ""}:
            return raw_value
    return default


def _get_csv_env_aliases(names: tuple[str, ...], default: list[str]) -> list[str]:
    for name in names:
        raw_value = os.getenv(name)
        if raw_value:
            return [item.strip() for item in raw_value.split(",") if item.strip()]
    return default


def _resolve_project_path(value: str | None, default: Path) -> Path:
    if not value:
        return default.resolve()

    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (PROJECT_ROOT / path).resolve()


@dataclass(frozen=True)
class Settings:
    project_name: str
    environment: str
    debug: bool
    api_v1_prefix: str
    backend_host: str
    backend_port: int
    database_url: str | None
    cors_allow_origins: list[str]
    saved_models_dir: Path
    active_model_metadata_file: Path
    default_model_version: str
    openai_api_key: str | None
    llm_provider: str
    enable_llm: bool
    llm_enabled: bool
    rag_enabled: bool
    use_mock_data: bool
    sap_integration_enabled: bool
    sap_base_url: str | None
    sap_portal_url: str | None
    sap_client: str | None
    sap_username: str | None
    sap_password: str | None
    sap_automation_headless: bool

    @classmethod
    def from_env(cls) -> "Settings":
        saved_models_dir = _resolve_project_path(
            _get_first_env("SAVED_MODELS_DIR", "MODEL_DIR"),
            BACKEND_DIR / "saved_models",
        )
        enable_llm = _get_bool_env(
            "ENABLE_LLM",
            default=_get_bool_env("LLM_ENABLED", default=False),
        )

        return cls(
            project_name=os.getenv("PROJECT_NAME", "predictive-maintenance-ai"),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=_get_bool_env("DEBUG", default=True),
            api_v1_prefix=_get_first_env("API_V1_PREFIX", "API_PREFIX", default="/api/v1") or "/api/v1",
            backend_host=os.getenv("BACKEND_HOST", "0.0.0.0"),
            backend_port=int(os.getenv("BACKEND_PORT", "8000")),
            database_url=os.getenv("DATABASE_URL"),
            cors_allow_origins=_get_csv_env_aliases(
                ("CORS_ORIGINS", "CORS_ALLOW_ORIGINS"),
                default=[
                    "http://localhost:3000",
                    "http://localhost:5173",
                    "http://localhost:8501",
                ],
            ),
            saved_models_dir=saved_models_dir,
            active_model_metadata_file=_resolve_project_path(
                _get_first_env("ACTIVE_MODEL_METADATA_FILE"),
                saved_models_dir / "active_model.json",
            ),
            default_model_version=os.getenv("DEFAULT_MODEL_VERSION", "unavailable"),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            llm_provider=os.getenv("LLM_PROVIDER", "none"),
            enable_llm=enable_llm,
            llm_enabled=enable_llm,
            rag_enabled=_get_bool_env("RAG_ENABLED", default=False),
            use_mock_data=_get_bool_env("USE_MOCK_DATA", default=True),
            sap_integration_enabled=_get_bool_env(
                "SAP_INTEGRATION_ENABLED",
                default=False,
            ),
            sap_base_url=os.getenv("SAP_BASE_URL") or os.getenv("SAP_PORTAL_URL") or None,
            sap_portal_url=os.getenv("SAP_PORTAL_URL") or os.getenv("SAP_BASE_URL") or None,
            sap_client=os.getenv("SAP_CLIENT") or None,
            sap_username=os.getenv("SAP_USERNAME") or None,
            sap_password=os.getenv("SAP_PASSWORD") or None,
            sap_automation_headless=_get_bool_env(
                "SAP_AUTOMATION_HEADLESS",
                default=False,
            ),
        )

    @property
    def async_database_url(self) -> str | None:
        if not self.database_url:
            return None

        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url

        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )

        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)

        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
