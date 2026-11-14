"""Translate persisted canonical measurements into deterministic analytics."""

from __future__ import annotations

import json
import logging
import os
from threading import RLock
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from analytics.engine import ALGORITHM_VERSION, AnalyticsConfig, MetricReading, UNITS, analyze_history
from . import models
from .service import dump

logger = logging.getLogger(__name__)
_materialize_lock = RLock()
_VALID_STATUSES = {"INSUFFICIENT_BASELINE", "CANDIDATE_DEVIATION", "VALID"}

def _analytics_config() -> AnalyticsConfig:
    defaults=AnalyticsConfig()
    return AnalyticsConfig(
        history_window=int(os.getenv("ANALYTICS_HISTORY_WINDOW",defaults.history_window)),
        minimum_baseline=int(os.getenv("ANALYTICS_MINIMUM_BASELINE",defaults.minimum_baseline)),
        robust_z_threshold=float(os.getenv("ANALYTICS_ROBUST_Z_THRESHOLD",defaults.robust_z_threshold)),
        baseline_guard_z=float(os.getenv("ANALYTICS_BASELINE_GUARD_Z",defaults.baseline_guard_z)),
        ewma_alpha=float(os.getenv("ANALYTICS_EWMA_ALPHA",defaults.ewma_alpha)),
        ewma_z_threshold=float(os.getenv("ANALYTICS_EWMA_Z_THRESHOLD",defaults.ewma_z_threshold)),
        required_consecutive=int(os.getenv("ANALYTICS_REQUIRED_CONSECUTIVE",defaults.required_consecutive)),
        dispersion_floors=defaults.dispersion_floors,
    )


def materialize_analytics(db: Session, mission_id: str, astronaut_id: str) -> dict[str, Any]:
    """Recompute from canonical SQLite history and idempotently materialize alerts.

    The bounded MVP history is small, so a deterministic rebuild on the existing
    summary/alerts reads is simpler and restart-safe. Observation UUIDs are stable
    for the same algorithm version and supporting samples; SQLite upserts prevent
    parallel summary/alerts requests from inserting duplicates.
    """
    with _materialize_lock:
        config=_analytics_config()
        records = db.scalars(select(models.ResourceRow).where(
            models.ResourceRow.kind == "measurement",
            models.ResourceRow.mission_id == mission_id,
            models.ResourceRow.astronaut_id == astronaut_id,
        ).order_by(models.ResourceRow.event_at, models.ResourceRow.id)).all()
        health_rows = db.scalars(select(models.SensorHealthRow).where(
            models.SensorHealthRow.measurement_id.in_([row.id for row in records])
        )).all() if records else []
        health_by_measurement: dict[str, dict[str, dict[str, Any]]] = {}
        for row in health_rows:
            payload = json.loads(row.payload_json)
            health_by_measurement.setdefault(row.measurement_id, {})[payload["channel"]] = payload

        readings: list[MetricReading] = []
        contexts: set[str] = set()
        for row in records:
            payload = json.loads(row.payload_json)
            context = payload.get("activity_context", "UNKNOWN")
            contexts.add(context)
            source = (payload.get("provenance") or {}).get("source_format", "unknown_source")
            for metric in UNITS:
                value = payload.get(metric)
                if not isinstance(value, dict):
                    readings.append(MetricReading(astronaut_id, payload.get("observed_at", ""), metric, None, UNITS[metric], "invalid", context, source, row.id))
                    continue
                sensor = health_by_measurement.get(row.id, {}).get(metric, {})
                readings.append(MetricReading(
                    astronaut_id=astronaut_id,
                    timestamp=payload.get("observed_at", ""),
                    metric=metric,
                    value=value.get("value"),
                    unit=value.get("unit", ""),
                    quality=value.get("quality", "invalid"),
                    activity_context=context,
                    source=source,
                    reading_id=row.id,
                    connectivity=sensor.get("connectivity", "unknown"),
                ))

        result = analyze_history(readings,config)
        for observation in result.observations:
            observation["mission_id"] = mission_id

        # Return explicit warm-up status for every metric/context. No missing
        # values are fabricated; zero valid samples means an empty baseline.
        contexts = contexts or {"UNKNOWN"}
        evaluations: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for evaluation in result.evaluations:
            evaluations.setdefault((evaluation.get("metric", ""), evaluation.get("activity_context", "UNKNOWN")), []).append(evaluation)
        summaries_by_scope = {(item["metric"], item["activity_context"]): item for item in result.summaries}
        summaries: list[dict[str, Any]] = []
        for context in sorted(contexts):
            for metric in UNITS:
                existing = summaries_by_scope.get((metric, context))
                if existing:
                    summary = dict(existing)
                else:
                    metric_evaluations = evaluations.get((metric, context), [])
                    valid_count = sum(item.get("status") in _VALID_STATUSES for item in metric_evaluations)
                    summary = {
                        "metric": metric, "activity_context": context,
                        "status": "INSUFFICIENT_BASELINE",
                        "valid_measurement_count": valid_count,
                        "baseline_sample_count": valid_count,
                        "baseline_median": None, "mad": None,
                    }
                summary["astronaut_id"] = astronaut_id
                summaries.append(summary)

        # Mark previously materialized observations inactive, then reactivate or
        # insert the deterministic current set. Historical acknowledgments remain.
        db.execute(update(models.StatisticalObservationRow).where(
            models.StatisticalObservationRow.mission_id == mission_id,
            models.StatisticalObservationRow.astronaut_id == astronaut_id,
        ).values(is_active=False))
        for observation in result.observations:
            row = db.get(models.StatisticalObservationRow, observation["id"])
            if row is None:
                row = models.StatisticalObservationRow(
                    id=observation["id"], mission_id=mission_id,
                    astronaut_id=astronaut_id, detected_at=observation["detected_at"],
                    metric=observation["metric"], activity_context=observation["activity_context"],
                    is_active=True, payload_json=dump(observation),
                )
                db.add(row)
            else:
                row.is_active = True
                row.payload_json = dump(observation)
        db.commit()
        latest = max((row.event_at for row in records), default=None)
        ready = any(item["status"] == "READY" for item in summaries)
        logger.info("Analytics materialized version=%s measurements=%d observations=%d baseline=%s", ALGORITHM_VERSION, len(records), len(result.observations), "ready" if ready else "insufficient_baseline")
        return {
            "astronaut_id": astronaut_id,
            "analytics_status": "ready",
            "baseline_status": "ready" if ready else "insufficient_baseline",
            "statistical_observations_count": len(result.observations),
            "latest_measurement_at": latest,
            "algorithm_version": ALGORITHM_VERSION,
            "configuration": {"history_window":config.history_window,"minimum_baseline":config.minimum_baseline,"robust_z_threshold":config.robust_z_threshold,"baseline_guard_z":config.baseline_guard_z,"ewma_alpha":config.ewma_alpha,"ewma_z_threshold":config.ewma_z_threshold,"required_consecutive":config.required_consecutive,"dispersion_floors":config.dispersion_floors},
            "metrics": summaries,
            "synthetic": True,
        }

