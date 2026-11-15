from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from analytics.engine import AnalyticsConfig, MetricReading, analyze_history


UNITS = {"heart_rate_bpm": "bpm", "spo2_percent": "percent", "respiratory_rate_per_min": "breaths/min"}


def reading(metric="heart_rate_bpm", value=70, *, astro="crew-a", activity="RESTING", quality="unverified", unit=None, at=None, rid=None, source="amina_simulator_v1", connectivity="unknown"):
    timestamp = datetime(2026, 11, 14, tzinfo=timezone.utc) if at is None else at
    if isinstance(timestamp, datetime):
        timestamp = timestamp.isoformat().replace("+00:00", "Z")
    return MetricReading(astro, timestamp, metric, value, unit or UNITS.get(metric, "bpm"), quality, activity, source, rid or f"{astro}:{metric}:{timestamp}", connectivity)


def series(metric, values, *, astro="crew-a", activity="RESTING", start=None):
    start = start or datetime(2026, 11, 14, tzinfo=timezone.utc)
    return [reading(metric, value, astro=astro, activity=activity, at=start + timedelta(minutes=i), rid=f"{astro}:{metric}:{activity}:{i}") for i, value in enumerate(values)]


@pytest.mark.parametrize(("metric", "values"), [
    ("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70, 71, 69, 70]),
    ("spo2_percent", [97, 98, 99, 98, 97, 99, 98, 98, 97, 99, 98]),
    ("respiratory_rate_per_min", [14, 15, 16, 15, 14, 16, 15, 15, 14, 16, 15]),
])
def test_stable_metric_series_build_personal_baselines(metric, values):
    result = analyze_history(series(metric, values))
    assert result.observations == []
    assert result.summaries[0]["status"] == "READY"
    assert result.summaries[0]["baseline_median"] == pytest.approx(values[5], abs=1)


@pytest.mark.parametrize("metric", list(UNITS))
def test_insufficient_baseline_is_explicit(metric):
    result = analyze_history(series(metric, [70, 71, 70, 69, 70]))
    assert result.observations == []
    assert result.summaries[0]["status"] == "INSUFFICIENT_BASELINE"
    assert all(item["status"] == "INSUFFICIENT_BASELINE" for item in result.evaluations)


@pytest.mark.parametrize(("metric", "baseline", "shift"), [
    ("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70], [90, 91, 92]),
    ("spo2_percent", [97, 98, 99, 98, 97, 99, 98, 98], [90, 89, 90]),
    ("respiratory_rate_per_min", [14, 15, 16, 15, 14, 16, 15, 15], [22, 23, 22]),
])
def test_sustained_personal_deviation_emits_explainable_observation(metric, baseline, shift):
    result = analyze_history(series(metric, baseline + shift))
    assert len(result.observations) == 1
    observation = result.observations[0]
    assert observation["metric"] == metric
    assert observation["status"] == "STATISTICAL_DEVIATION"
    assert observation["method"] in {"median_mad", "ewma"}
    assert len(observation["measurement_ids"]) == 3
    assert observation["supporting_values"]["baseline_sample_count"] >= 8
    assert "not a medical conclusion" in observation["explanation"]


def test_single_isolated_spike_does_not_emit_observation_or_contaminate_baseline():
    result = analyze_history(series("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70, 180, 70]))
    assert result.observations == []
    assert result.summaries[0]["baseline_median"] == pytest.approx(70)


def test_zero_mad_uses_documented_dispersion_floor_without_single_sample_alert():
    result = analyze_history(series("heart_rate_bpm", [70] * 8 + [73, 70]))
    assert result.observations == []
    assert result.summaries[0]["baseline_median"] == 70


@pytest.mark.parametrize(("value", "quality", "expected"), [
    (None, "missing", "MISSING_MEASUREMENT"),
    (None, "unverified", "INVALID_MEASUREMENT"),
    (float("nan"), "unverified", "INVALID_MEASUREMENT"),
    (float("inf"), "unverified", "INVALID_MEASUREMENT"),
    ("72", "unverified", "INVALID_MEASUREMENT"),
    (True, "unverified", "INVALID_MEASUREMENT"),
    (-1, "unverified", "INVALID_MEASUREMENT"),
    (101, "unverified", "INVALID_MEASUREMENT"),
])
def test_missing_and_invalid_values_never_enter_baseline(value, quality, expected):
    metric = "spo2_percent" if value == 101 else "heart_rate_bpm"
    result = analyze_history([reading(metric, value, quality=quality, rid="bad")])
    assert result.evaluations[0]["status"] == expected
    assert result.summaries == []


def test_wrong_units_and_naive_or_missing_timestamps_are_invalid():
    result = analyze_history([
        reading(unit="beats/min", rid="unit"),
        reading(at="2026-11-14T12:00:00", rid="naive"),
        reading(at="", rid="missing-time"),
    ])
    assert len(result.evaluations) == 3
    assert all(item["status"] == "INVALID_MEASUREMENT" for item in result.evaluations)


def test_source_reported_sensor_failure_is_separate_from_statistical_deviation():
    result = analyze_history([reading(connectivity="source_reported_disconnected", rid="disconnected")])
    assert result.evaluations[0]["status"] == "SENSOR_FAILURE"
    assert result.observations == []
    assert result.summaries == []


def test_zero_is_retained_as_a_numeric_value_when_contract_marks_it_valid():
    result = analyze_history(series("heart_rate_bpm", [0, 0, 0, 0, 0, 0, 0, 0]))
    assert result.summaries[0]["valid_measurement_count"] == 8
    assert result.summaries[0]["baseline_median"] == 0


def test_astronauts_and_activity_contexts_have_independent_baselines():
    records = series("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70], astro="crew-a")
    records += series("heart_rate_bpm", [119, 120, 121, 120, 119, 121, 120, 120], astro="crew-b")
    records += series("heart_rate_bpm", [49, 50, 51, 50, 49, 51, 50, 50], astro="crew-a", activity="EXERCISE")
    result = analyze_history(records)
    medians = {(item["astronaut_id"], item["activity_context"]): item["baseline_median"] for item in result.summaries}
    assert medians[("crew-a", "RESTING")] == 70
    assert medians[("crew-b", "RESTING")] == 120
    assert medians[("crew-a", "EXERCISE")] == 50


def test_out_of_order_readings_are_sorted_deterministically():
    ordered = series("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70, 90, 91, 92])
    forward = analyze_history(ordered)
    reverse = analyze_history(list(reversed(ordered)))
    assert [item["id"] for item in forward.observations] == [item["id"] for item in reverse.observations]


def test_exact_duplicate_reading_is_ignored_and_conflicting_duplicate_is_excluded():
    records = series("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70])
    exact = analyze_history(records + [records[0]])
    assert exact.duplicate_count == 1
    conflict = analyze_history(records + [reading(value=200, at=datetime(2026, 11, 14, tzinfo=timezone.utc), rid=records[0].reading_id)])
    assert conflict.summaries[0]["valid_measurement_count"] == 7
    assert conflict.summaries[0]["baseline_median"] is None
    assert sum(item["status"] == "INVALID_MEASUREMENT" for item in conflict.evaluations) == 2
    assert conflict.observations == []


def test_candidate_spike_does_not_corrupt_following_personal_baseline():
    result = analyze_history(series("heart_rate_bpm", [69, 70, 71, 70, 69, 71, 70, 70, 180, 70, 70]))
    assert result.observations == []
    assert result.summaries[0]["baseline_median"] == pytest.approx(70)


def test_config_parameters_are_validated():
    with pytest.raises(ValueError):
        AnalyticsConfig(ewma_alpha=0)
    with pytest.raises(ValueError):
        AnalyticsConfig(minimum_baseline=31)
