from __future__ import annotations

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def test_expected_sample_files_exist() -> None:
    expected = {
        "sample_sensor_data.csv",
        "sample_work_orders.csv",
        "sample_alarms.csv",
        "sample_checklists.csv",
        "sample_expert_notes.csv",
        "sample_feedback.csv",
    }

    assert expected <= {path.name for path in SAMPLE_DIR.iterdir()}


def test_sample_sensor_data_has_required_columns_and_assets() -> None:
    rows = _read_csv_rows(SAMPLE_DIR / "sample_sensor_data.csv")
    required_columns = {
        "timestamp",
        "asset_id",
        "asset_code",
        "vibration",
        "temperature",
        "pressure",
        "current_value",
        "speed",
        "flow",
        "runtime_hours",
    }
    expected_assets = {
        "FURNACE_001",
        "FEEDER_001",
        "IS_MACHINE_001",
        "ANNEALING_LEHR_001",
        "INSPECTION_001",
        "PACKAGING_001",
        "PALLETIZER_001",
        "CONVEYOR_001",
    }

    assert len(rows) >= 40
    assert required_columns <= set(rows[0])
    assert expected_assets <= {row["asset_code"] for row in rows}


def test_knowledge_sample_files_have_searchable_columns() -> None:
    work_orders = _read_csv_rows(SAMPLE_DIR / "sample_work_orders.csv")
    expert_notes = _read_csv_rows(SAMPLE_DIR / "sample_expert_notes.csv")
    checklists = _read_csv_rows(SAMPLE_DIR / "sample_checklists.csv")

    assert {"asset_id", "asset_code", "summary", "action_taken"} <= set(work_orders[0])
    assert {"asset_id", "asset_code", "summary", "recommended_action"} <= set(expert_notes[0])
    assert {"asset_id", "asset_code", "summary", "checklist_item"} <= set(checklists[0])


def test_sample_feedback_has_learning_columns() -> None:
    rows = _read_csv_rows(SAMPLE_DIR / "sample_feedback.csv")

    assert len(rows) >= 10
    assert {
        "feedback_id",
        "asset_id",
        "asset_code",
        "prediction_id",
        "feedback_date",
        "was_prediction_correct",
        "actual_failure_happened",
        "actual_failure_mode",
        "action_taken",
        "timing_feedback",
        "technician_comment",
    } <= set(rows[0])
