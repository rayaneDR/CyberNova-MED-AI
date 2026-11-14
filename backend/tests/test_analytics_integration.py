from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import uuid

from sqlalchemy import select

from backend.app.db import SessionLocal
from backend.app.models import ResourceRow, SensorHealthRow, StatisticalObservationRow


def _session(seeded, source_format):
    return next(item for item in seeded["sessions"] if item["source_format"] == source_format)


def _ingest_series(client, seeded, packet, points):
    source = _session(seeded, "amina_simulator_v1")
    endpoint = f"/ingest/simulator?source_session_id={source['source_session_id']}"
    start = datetime(2026, 11, 14, 14, 0, tzinfo=timezone.utc)
    receipts = []
    for index, (hr, spo2, rr, mode) in enumerate(points, start=1):
        item = deepcopy(packet)
        observed = (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z")
        context = item["ingestion_payload_contract"]["ingestion_context"]
        context["payload_id"] = f"analytics-test-{uuid.uuid4()}"
        context["timestamp_utc"] = observed
        item["simulator"]["sequence"] = index
        item["simulator"]["sent_at"] = observed
        item["simulator"]["mode"] = mode
        sensors = item["ingestion_payload_contract"]["telemetry_sensors"]
        sensors["heart_rate_bpm"]["value"] = hr
        sensors["spo2_percent"]["value"] = spo2
        sensors["spo2_percent"]["spo2"] = spo2
        sensors["respiratory_rate_rpm"]["value"] = rr
        sensors["respiratory_rate_rpm"]["respiratory_rate"] = rr
        response = client.post(endpoint, json=item)
        assert response.status_code == 201, response.text
        receipts.append(response.json())
    return source, receipts


def test_summary_reports_insufficient_baseline_without_fabricating_alerts(client, seeded):
    astronaut = _session(seeded, "amina_simulator_v1")["astronaut_id"]
    query = {"mission_id": seeded["mission_id"], "astronaut_id": astronaut}
    summary = client.get("/analytics/summary", params=query).json()
    alerts = client.get("/alerts", params=query).json()
    assert summary["analytics_status"] == "ready"
    assert summary["baseline_status"] == "insufficient_baseline"
    assert summary["statistical_observations_count"] == 0
    assert len(summary["metrics"]) == 3
    assert {item["status"] for item in summary["metrics"]} == {"INSUFFICIENT_BASELINE"}
    assert all(item["baseline_sample_count"] == 0 for item in summary["metrics"])
    assert alerts["items"] == [] and alerts["baseline_status"] == "insufficient_baseline"


def test_sustained_simulator_deviation_materializes_once_and_survives_restart(client, seeded, packet):
    baseline = [(hr, spo2, rr, "normal") for hr, spo2, rr in zip(
        [69, 70, 71, 70, 69, 71, 70, 70],
        [97, 98, 99, 98, 97, 99, 98, 98],
        [14, 15, 16, 15, 14, 16, 15, 15],
    )]
    source, _ = _ingest_series(client, seeded, packet, baseline + [(90, 90, 22, "anomaly"), (91, 89, 23, "anomaly"), (92, 90, 22, "anomaly")])
    query = {"mission_id": seeded["mission_id"], "astronaut_id": source["astronaut_id"]}
    summary = client.get("/analytics/summary", params=query).json()
    alerts = client.get("/alerts", params={**query, "kind": "statistical_observation"}).json()
    assert summary["baseline_status"] == "ready"
    assert summary["statistical_observations_count"] == 3
    assert len(alerts["items"]) == 3
    assert {item["statistical_observation"]["metric"] for item in alerts["items"]} == {"heart_rate_bpm", "spo2_percent", "respiratory_rate_per_min"}
    assert all(len(item["statistical_observation"]["measurement_ids"]) == 3 for item in alerts["items"])
    ids = {item["id"] for item in alerts["items"]}
    client.get("/analytics/summary", params=query)
    client.get("/alerts", params=query)
    with SessionLocal() as db:
        assert len(db.scalars(select(StatisticalObservationRow).where(StatisticalObservationRow.astronaut_id == source["astronaut_id"], StatisticalObservationRow.is_active.is_(True))).all()) == 3
    with client.__class__(client.app) as restarted:
        after = restarted.get("/alerts", params={**query, "kind": "statistical_observation"}).json()["items"]
        assert {item["id"] for item in after} == ids
        ack = restarted.patch(f"/alerts/{after[0]['id']}/acknowledge", json={"acknowledged": True, "note": "Reviewed statistical evidence"})
        assert ack.status_code == 200, ack.text
    with client.__class__(client.app) as restarted:
        persisted = restarted.get("/alerts", params={**query, "acknowledged": True}).json()["items"]
        assert len(persisted) == 1
        assert persisted[0]["acknowledgment"]["note"] == "Reviewed statistical evidence"


def test_isolated_simulator_spike_is_not_materialized(client, seeded, packet):
    points = [(70, 98, 15, "normal")] * 8 + [(180, 98, 15, "anomaly"), (70, 98, 15, "normal")]
    source, _ = _ingest_series(client, seeded, packet, points)
    query = {"mission_id": seeded["mission_id"], "astronaut_id": source["astronaut_id"]}
    assert client.get("/analytics/summary", params=query).json()["statistical_observations_count"] == 0
    assert client.get("/alerts", params={**query, "kind": "statistical_observation"}).json()["items"] == []


def test_missing_sensor_stays_a_sensor_issue_and_does_not_enter_baseline(client, seeded, packet):
    source, _ = _ingest_series(client, seeded, packet, [(70 + i % 2, 98, 15, "normal") for i in range(8)])
    broken = deepcopy(packet)
    context = broken["ingestion_payload_contract"]["ingestion_context"]
    context["payload_id"] = f"analytics-missing-{uuid.uuid4()}"
    context["timestamp_utc"] = "2026-11-14T15:00:00Z"
    broken["simulator"]["sequence"] = 9
    broken["simulator"]["sent_at"] = context["timestamp_utc"]
    broken["ingestion_payload_contract"]["telemetry_sensors"]["heart_rate_bpm"]["value"] = None
    result = client.post(f"/ingest/simulator?source_session_id={source['source_session_id']}", json=broken)
    assert result.status_code == 201, result.text
    query = {"mission_id": seeded["mission_id"], "astronaut_id": source["astronaut_id"]}
    alerts = client.get("/alerts", params=query).json()["items"]
    assert any(item["kind"] == "sensor_data_issue" and "VALUE_MISSING" in item["sensor_health"]["issue_codes"] for item in alerts)
    assert all(item["kind"] != "statistical_observation" for item in alerts)
    summary = client.get("/analytics/summary", params=query).json()
    heart_rate = next(item for item in summary["metrics"] if item["metric"] == "heart_rate_bpm")
    assert heart_rate["valid_measurement_count"] == 8


def test_canonical_measurement_write_persists_sensor_quality_without_fake_connectivity(client, seeded):
    source = _session(seeded, "canonical_v1")
    now = "2026-11-14T14:00:00Z"
    body = {
        "astronaut_id": source["astronaut_id"], "mission_id": seeded["mission_id"], "mission_day": 1,
        "observed_at": now, "synthetic": True, "activity_context": "RESTING",
        "heart_rate_bpm": {"value": 70.0, "unit": "bpm", "quality": "unverified", "source_paths": ["test.hr"]},
        "spo2_percent": {"value": 98.0, "unit": "percent", "quality": "unverified", "source_paths": ["test.spo2"]},
        "respiratory_rate_per_min": {"value": 15.0, "unit": "breaths/min", "quality": "unverified", "source_paths": ["test.rr"]},
    }
    response = client.post(f"/measurements?input_format=canonical_v1&source_session_id={source['source_session_id']}", json=body, headers={"Idempotency-Key": str(uuid.uuid4())})
    assert response.status_code == 201, response.text
    measurement = client.get("/measurements", params={"mission_id": seeded["mission_id"], "astronaut_id": source["astronaut_id"]}).json()
    assert len(measurement["sensor_health"]) == 3
    assert all(item["connectivity"] == "unknown" and item["quality"] == "unverified" and item["issue_codes"] == [] for item in measurement["sensor_health"])

