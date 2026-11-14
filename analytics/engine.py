"""Explainable, non-clinical personal-baseline analysis of canonical telemetry."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
import statistics
from typing import Any, Iterable, Literal
from uuid import NAMESPACE_URL, uuid5

Metric = Literal["heart_rate_bpm", "spo2_percent", "respiratory_rate_per_min"]
Quality = Literal["unverified", "missing", "invalid", "conflict"]
ACTIVITIES = frozenset({"RESTING", "SLEEP", "EXERCISE", "EVA_PREP", "EVA_ACTIVE", "LAB_WORK", "UNKNOWN"})
UNITS: dict[str, str] = {"heart_rate_bpm": "bpm", "spo2_percent": "percent", "respiratory_rate_per_min": "breaths/min"}
ALGORITHM_VERSION = "personal-baseline-mad-ewma-v1"


@dataclass(frozen=True, slots=True)
class AnalyticsConfig:
    history_window: int = 30
    minimum_baseline: int = 8
    robust_z_threshold: float = 3.5
    baseline_guard_z: float = 2.5
    ewma_alpha: float = 0.25
    ewma_z_threshold: float = 3.0
    required_consecutive: int = 3
    dispersion_floors: dict[str, float] = field(default_factory=lambda: {
        "heart_rate_bpm": 1.0,
        "spo2_percent": 0.1,
        "respiratory_rate_per_min": 1.0,
    })

    def __post_init__(self) -> None:
        if self.history_window < 1 or self.minimum_baseline < 2 or self.minimum_baseline > self.history_window:
            raise ValueError("Require 2 <= minimum_baseline <= history_window")
        if not 0 < self.ewma_alpha <= 1:
            raise ValueError("ewma_alpha must be in (0, 1]")
        if self.required_consecutive < 2:
            raise ValueError("required_consecutive must be at least 2")
        if min(self.robust_z_threshold, self.baseline_guard_z, self.ewma_z_threshold) <= 0:
            raise ValueError("Statistical parameters must be positive")
        if set(self.dispersion_floors) != set(UNITS) or any(not math.isfinite(v) or v <= 0 for v in self.dispersion_floors.values()):
            raise ValueError("Provide a finite positive dispersion floor for every metric")


@dataclass(frozen=True, slots=True)
class MetricReading:
    astronaut_id: str
    timestamp: str
    metric: str
    value: Any
    unit: str
    quality: str
    activity_context: str
    source: str
    reading_id: str
    connectivity: str = "unknown"


@dataclass(slots=True)
class AnalyticsResult:
    evaluations: list[dict[str, Any]]
    observations: list[dict[str, Any]]
    summaries: list[dict[str, Any]]
    duplicate_count: int = 0

    @property
    def has_baseline(self) -> bool:
        return any(item["status"] == "READY" for item in self.summaries)


def _median_mad(values: list[float]) -> tuple[float, float]:
    center = statistics.median(values)
    return center, statistics.median(abs(value - center) for value in values)


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _validate(reading: MetricReading) -> tuple[datetime | None, str | None]:
    if not isinstance(reading, MetricReading):
        return None, "reading must be a MetricReading"
    if not isinstance(reading.astronaut_id, str) or not reading.astronaut_id.strip():
        return None, "astronaut_id is required"
    if not isinstance(reading.reading_id, str) or not reading.reading_id.strip():
        return None, "reading_id is required"
    if reading.metric not in UNITS:
        return None, "unsupported metric"
    if reading.unit != UNITS[reading.metric]:
        return None, f"{reading.metric} requires unit {UNITS[reading.metric]}"
    if reading.activity_context not in ACTIVITIES:
        return None, "unsupported activity_context"
    if not isinstance(reading.source, str) or not reading.source.strip():
        return None, "source is required"
    if reading.quality not in {"unverified", "missing", "invalid", "conflict"}:
        return None, "unsupported quality"
    try:
        timestamp = _parse_timestamp(reading.timestamp)
    except (TypeError, ValueError, OverflowError) as exc:
        return None, str(exc)
    if reading.connectivity == "source_reported_disconnected":
        return timestamp, "SENSOR_FAILURE"
    if reading.quality == "missing":
        if reading.value is not None:
            return timestamp, "missing quality requires a null value"
        return timestamp, "MISSING_MEASUREMENT"
    if reading.quality in {"invalid", "conflict"}:
        if reading.value is not None:
            return timestamp, f"{reading.quality} quality requires a null value"
        return timestamp, "INVALID_MEASUREMENT"
    if reading.value is None:
        return timestamp, "unverified quality requires a numeric value"
    if isinstance(reading.value, bool) or not isinstance(reading.value, (int, float)):
        return timestamp, "value must be a JSON number (numeric strings and booleans are rejected)"
    if not math.isfinite(float(reading.value)):
        return timestamp, "value must be finite"
    if float(reading.value) < 0:
        return timestamp, "value must be nonnegative"
    if reading.metric == "spo2_percent" and float(reading.value) > 100:
        return timestamp, "spo2_percent must be between 0 and 100"
    return timestamp, None


def _stable_id(namespace: str) -> str:
    return str(uuid5(NAMESPACE_URL, namespace))


def analyze_history(readings: Iterable[MetricReading], config: AnalyticsConfig | None = None) -> AnalyticsResult:
    """Validate, de-duplicate, order, and analyze readings in isolated scopes.

    Exact duplicate IDs are ignored. Conflicting content under one reading ID is
    rejected, since choosing either copy would make results input-order dependent.
    Invalid/missing/disconnected values are returned as evaluations and excluded
    from all baselines.
    """
    cfg = config or AnalyticsConfig()
    accepted: dict[tuple[str, str, str, str], tuple[MetricReading, datetime]] = {}
    rejected: list[tuple[MetricReading, str]] = []
    conflicted_ids: set[tuple[str, str, str, str]] = set()
    duplicates = 0
    for item in readings:
        when, issue = _validate(item)
        if issue:
            rejected.append((item, issue))
            continue
        assert when is not None
        duplicate_key = (item.astronaut_id, item.metric, item.activity_context, item.reading_id)
        if duplicate_key in conflicted_ids:
            rejected.append((item, "duplicate reading_id has conflicting content"))
            continue
        previous = accepted.get(duplicate_key)
        if previous is not None:
            if previous[0] != item:
                accepted.pop(duplicate_key)
                conflicted_ids.add(duplicate_key)
                rejected.append((previous[0], "duplicate reading_id has conflicting content"))
                rejected.append((item, "duplicate reading_id has conflicting content"))
            else:
                duplicates += 1
            continue
        accepted[duplicate_key] = (item, when)

    scopes: dict[tuple[str, str, str], list[tuple[MetricReading, datetime]]] = defaultdict(list)
    for reading, when in accepted.values():
        scopes[(reading.astronaut_id, reading.metric, reading.activity_context)].append((reading, when))
    evaluations: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for scope, ordered in sorted(scopes.items()):
        astronaut_id, metric, activity = scope
        ordered.sort(key=lambda pair: (pair[1], pair[0].reading_id))
        baseline: list[tuple[str, float, str]] = []
        ewma: float | None = None
        candidate_run: list[tuple[MetricReading, float, float, float, float, int, str]] = []
        episode_reported = False
        for reading, when in ordered:
            value = float(reading.value)
            if len(baseline) < cfg.minimum_baseline:
                baseline.append((reading.reading_id, value, reading.source))
                ewma = value if ewma is None else cfg.ewma_alpha * value + (1 - cfg.ewma_alpha) * ewma
                evaluations.append({"reading_id": reading.reading_id, "metric": metric, "activity_context": activity, "status": "INSUFFICIENT_BASELINE", "baseline_sample_count": len(baseline), "reason": "Not enough prior valid measurements for a personal baseline."})
                continue

            window = baseline[-cfg.history_window:]
            values = [entry[1] for entry in window]
            center, mad = _median_mad(values)
            scale = max(1.4826 * mad, cfg.dispersion_floors[metric])
            robust_score = (value - center) / scale
            ewma = value if ewma is None else cfg.ewma_alpha * value + (1 - cfg.ewma_alpha) * ewma
            ewma_score = (ewma - center) / scale
            same_direction = (value - center) * (ewma - center) > 0
            robust_candidate = abs(robust_score) >= cfg.robust_z_threshold
            ewma_candidate = abs(ewma_score) >= cfg.ewma_z_threshold and same_direction and abs(robust_score) >= cfg.baseline_guard_z
            candidate = robust_candidate or ewma_candidate
            baseline_guard = abs(robust_score) >= cfg.baseline_guard_z
            baseline_ids = [entry[0] for entry in window]
            baseline_id = _stable_id(f"{ALGORITHM_VERSION}:{astronaut_id}:{metric}:{activity}:{'|'.join(baseline_ids)}")
            if candidate:
                candidate_run.append((reading, robust_score, ewma, ewma_score, mad, len(window), baseline_id))
                evaluations.append({"reading_id": reading.reading_id, "metric": metric, "activity_context": activity, "status": "CANDIDATE_DEVIATION", "baseline_sample_count": len(window), "robust_score": robust_score, "ewma_score": ewma_score})
                if len(candidate_run) >= cfg.required_consecutive and not episode_reported:
                    episode = candidate_run[:cfg.required_consecutive]
                    supporting = [entry[0].reading_id for entry in episode]
                    latest, latest_robust, latest_ewma, latest_ewma_score, latest_mad, n, episode_baseline = episode[-1]
                    robust_hit = any(abs(entry[1]) >= cfg.robust_z_threshold for entry in episode)
                    ewma_hit = any(abs(entry[3]) >= cfg.ewma_z_threshold for entry in episode)
                    observation_type = "combined_deviation" if robust_hit and ewma_hit else "robust_deviation" if robust_hit else "sustained_ewma_shift"
                    method = "median_mad" if robust_hit else "ewma"
                    observation_id = _stable_id(f"cybernova:{ALGORITHM_VERSION}:{astronaut_id}:{metric}:{activity}:{'|'.join(supporting)}")
                    observations.append({
                        "id": observation_id, "astronaut_id": astronaut_id,
                        "mission_id": "", "measurement_ids": supporting,
                        "detected_at": latest.timestamp, "activity_context": activity,
                        "metric": metric, "method": method,
                        "observation_type": observation_type, "status": "STATISTICAL_DEVIATION",
                        "algorithm_version": ALGORITHM_VERSION, "baseline_id": episode_baseline,
                        "score": abs(latest_robust) if robust_hit else abs(latest_ewma_score),
                        "source": latest.source, "quality": "unverified", "synthetic": True,
                        "explanation": f"{metric} showed a sustained statistical deviation from this astronaut's {activity} personal baseline across {cfg.required_consecutive} consecutive valid samples. This is a statistical observation, not a medical conclusion.",
                        "supporting_values": {
                            "baseline_sample_count": n, "baseline_median": center,
                            "mad": latest_mad, "robust_scale": scale,
                            "robust_score": latest_robust, "ewma_value": latest_ewma,
                            "ewma_score": latest_ewma_score,
                            "robust_z_threshold": cfg.robust_z_threshold,
                            "ewma_z_threshold": cfg.ewma_z_threshold,
                        },
                    })
                    episode_reported = True
            else:
                candidate_run = []
                episode_reported = False
                evaluations.append({"reading_id": reading.reading_id, "metric": metric, "activity_context": activity, "status": "VALID", "baseline_sample_count": len(window), "robust_score": robust_score, "ewma_score": ewma_score})
            if not baseline_guard and not candidate:
                baseline.append((reading.reading_id, value, reading.source))
                baseline = baseline[-cfg.history_window:]

        if baseline:
            center, mad = _median_mad([entry[1] for entry in baseline[-cfg.history_window:]])
            status = "READY" if len(baseline) >= cfg.minimum_baseline else "INSUFFICIENT_BASELINE"
            summaries.append({"astronaut_id": astronaut_id, "metric": metric, "activity_context": activity, "status": status, "valid_measurement_count": len(ordered), "baseline_sample_count": len(baseline), "baseline_median": center if status == "READY" else None, "mad": mad if status == "READY" else None})

    for reading, issue in rejected:
        if issue == "MISSING_MEASUREMENT":
            status = issue
        elif issue == "SENSOR_FAILURE":
            status = issue
        else:
            status = "INVALID_MEASUREMENT"
        evaluations.append({"reading_id": getattr(reading, "reading_id", ""), "metric": getattr(reading, "metric", ""), "activity_context": getattr(reading, "activity_context", "UNKNOWN"), "status": status, "reason": issue})

    evaluations.sort(key=lambda item: (item.get("reading_id", ""), item.get("metric", ""), item.get("status", "")))
    observations.sort(key=lambda item: (item["detected_at"], item["id"]))
    summaries.sort(key=lambda item: (item["astronaut_id"], item["metric"], item["activity_context"]))
    return AnalyticsResult(evaluations, observations, summaries, duplicates)
