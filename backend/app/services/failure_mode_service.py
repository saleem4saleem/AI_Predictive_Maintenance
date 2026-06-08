from __future__ import annotations


def detect_failure_mode(features: dict[str, float], rule_causes: list[str] | None = None) -> str:
    if features["vibration"] >= 7 and features["temperature"] >= 80:
        return "bearing wear / misalignment / lubrication issue"
    if features["pressure"] <= 5 and features["flow"] <= 50:
        return "blockage / leakage / pump degradation"
    if features["current_value"] >= 180 and features["speed"] <= 80:
        return "motor overload / mechanical blockage / drive issue"
    if features["flow"] <= 45:
        return "flow restriction or conveyor transfer issue"
    if rule_causes:
        return rule_causes[0]
    return "condition drift requiring inspection"
