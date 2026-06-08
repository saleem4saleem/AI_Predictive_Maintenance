from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_asset_id() -> int:
    return 1


@pytest.fixture
def attention_asset_id() -> int:
    return 6


@pytest.fixture
def invalid_asset_id() -> int:
    return 999999


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))
