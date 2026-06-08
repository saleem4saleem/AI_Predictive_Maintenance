from __future__ import annotations

from app.ml.training_data_builder import load_feedback_training_data


def test_load_feedback_training_data_reads_csv(tmp_path) -> None:
    feedback_path = tmp_path / "feedback.csv"
    feedback_path.write_text(
        "\n".join(
            [
                "feedback_id,asset_id,asset_code,prediction_id,feedback_date,was_prediction_correct,actual_failure_happened,actual_failure_mode,action_taken,timing_feedback,technician_comment",
                "FB-TEST,6,PACKAGING_001,101,2026-05-12T13:35:00+00:00,true,true,suction cup wear,Replaced suction cups,correct,Matched issue",
            ]
        ),
        encoding="utf-8",
    )

    dataframe = load_feedback_training_data(feedback_path)

    assert len(dataframe) == 1
    assert dataframe.loc[0, "asset_code"] == "PACKAGING_001"


def test_load_feedback_training_data_returns_empty_dataframe_when_missing(tmp_path) -> None:
    dataframe = load_feedback_training_data(tmp_path / "missing.csv")

    assert dataframe.empty
    assert "feedback_id" in dataframe.columns
