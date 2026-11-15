import json, uuid, subprocess, sys
from pathlib import Path
from backend.app.models import ResourceRow
from backend.app.db import SessionLocal

def test_health_and_docs(client):
    assert client.get("/health").json()=={"status":"ok","contract_version":"1.0.0","storage":"ready","analytics":"ready","synthetic_only":True}
    assert client.get("/docs").status_code==200

def test_astronaut_roster(client,seeded):
    roster=client.get("/astronauts",params={"mission_id":seeded["mission_id"]})
    assert roster.status_code==200 and len(roster.json()["items"])==3
    assert {a["aliases"][0]["value"] for a in roster.json()["items"]}=={"AST-001","AST-01","demo-crew-01"}

def test_seed_and_simulator_idempotency(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    url=f"/ingest/simulator?source_session_id={session['source_session_id']}"
    first=client.post(url,json=packet); second=client.post(url,json=packet)
    assert first.status_code==201,first.text
    assert second.status_code==200 and second.json()["duplicate"] is True
    q=f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}"
    measurements=client.get(q).json()
    assert len(measurements["items"])==1
    item=measurements["items"][0]
    assert item["heart_rate_bpm"]["value"]==71
    assert item["spo2_percent"]["source_paths"]==["telemetry_sensors.spo2_percent.value","telemetry_sensors.spo2_percent.spo2"]
    assert item["provenance"]["source_record_id"]==packet["ingestion_payload_contract"]["ingestion_context"]["payload_id"]
    assert len(measurements["sensor_health"])==3

def test_conflicting_aliases_quarantined(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    packet["ingestion_payload_contract"]["telemetry_sensors"]["spo2_percent"]["spo2"]=96
    result=client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",json=packet)
    assert result.status_code==201
    got=client.get(f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}").json()["items"][0]
    assert got["spo2_percent"]["value"] is None and got["spo2_percent"]["quality"]=="conflict"

def test_actual_simulator_anomaly_cli_packet(client,seeded):
    script=Path(r"C:\Users\rayan\Downloads\simu (1).py")
    result=subprocess.run([sys.executable,str(script),"--mode","anomaly","--scenario","tachycardia","--count","1","--interval","0","--dry-run","--seed","42","--quiet"],capture_output=True,text=True,check=True)
    packet=json.loads(result.stdout.strip().splitlines()[-1])
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    response=client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",json=packet)
    assert response.status_code==201,response.text
    got=client.get(f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}").json()["items"][0]
    assert got["heart_rate_bpm"]["value"] is not None and got["synthetic"] is True

def test_simulator_failure_mode_does_not_mark_unfaulted_core_channels_failed(client,seeded):
    script=Path(r"C:\Users\rayan\Downloads\simu (1).py")
    result=subprocess.run([sys.executable,str(script),"--mode","failure","--fault","dropout","--count","1","--interval","0","--dry-run","--seed","42","--quiet"],capture_output=True,text=True,check=True)
    packet=json.loads(result.stdout.strip().splitlines()[-1])
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    response=client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",json=packet)
    assert response.status_code==201,response.text
    got=client.get(f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}").json()["items"][0]
    assert all(got[k]["quality"]=="unverified" for k in ("heart_rate_bpm","spo2_percent","respiratory_rate_per_min"))

def test_missing_sensor_not_fabricated(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    packet["ingestion_payload_contract"]["telemetry_sensors"]["heart_rate_bpm"]["value"]=None
    r=client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",json=packet)
    assert r.status_code==201
    q=f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}"
    sample=client.get(q).json()["items"][0]
    assert sample["heart_rate_bpm"]["value"] is None and sample["heart_rate_bpm"]["quality"]=="missing"
    alerts=client.get(f"/alerts?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}").json()["items"]
    issue=next(x for x in alerts if "VALUE_MISSING" in x["sensor_health"]["issue_codes"])
    ack=client.patch(f"/alerts/{issue['id']}/acknowledge",json={"acknowledged":True,"note":"Reviewed sensor data"})
    assert ack.status_code==200 and ack.json()["item"]["acknowledgment"]["actor_id"]=="local-operator"

def test_duplicate_id_changed_body_conflicts(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1"); url=f"/ingest/simulator?source_session_id={session['source_session_id']}"
    assert client.post(url,json=packet).status_code==201
    packet["simulator"]["anomaly_ramp"]=0.2
    assert client.post(url,json=packet).status_code==409

def test_source_snapshot_and_separate_alias(client,seeded):
    path=Path(r"C:\Users\rayan\Downloads\raw_measurements.json")
    raw=path.read_bytes(); source=next(x for x in seeded["sessions"] if x["source_format"]=="ayoub_raw_v1")
    r=client.post(f"/measurements?source_session_id={source['source_session_id']}&input_format=ayoub_raw_v1",content=raw,headers={"Content-Type":"application/json"})
    assert r.status_code==201,r.text
    payload=r.json(); assert len(payload["measurement_ids"])==1 and len(payload["checkin_ids"])==1
    item=client.get(f"/checkins?mission_id={seeded['mission_id']}&astronaut_id={source['astronaut_id']}").json()["items"][0]
    assert item["report_kind"]=="source_snapshot" and item["fatigue"]["scale"]=="samn_perelli_1_7"
    sim=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    assert sim["astronaut_id"]!=source["astronaut_id"]

def test_unresolved_alias_rejected(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1"); packet["ingestion_payload_contract"]["ingestion_context"]["astronaut_id"]="AST-001"
    assert client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",json=packet).status_code==422

def test_duplicate_json_key_rejected(client,seeded):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    r=client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",content=b'{"project":"a","project":"b"}',headers={"Content-Type":"application/json"})
    assert r.status_code==400

def test_analytics_warmup_state(client,seeded):
    astronaut=seeded["sessions"][0]["astronaut_id"]
    result=client.get(f"/analytics/summary?mission_id={seeded['mission_id']}&astronaut_id={astronaut}").json()
    assert result["analytics_status"]=="ready" and result["baseline_status"]=="insufficient_baseline"
    assert result["statistical_observations_count"]==0 and len(result["metrics"])==3
    assert all(item["status"]=="INSUFFICIENT_BASELINE" for item in result["metrics"])

def test_radiation_quantity_boundary(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    r=client.post(f"/ingest/simulator?source_session_id={session['source_session_id']}",json=packet); assert r.status_code==201
    base=f"mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}"
    all_items=client.get(f"/radiation?{base}").json()["items"]
    assert all(x["quantity"] not in ("source_dose_rate_msv_day","source_cumulative_dose_msv") for x in all_items)
    rates=client.get(f"/radiation?{base}&quantity=source_dose_rate_msv_day").json()["items"]
    assert rates[0]["value"]==0.53 and rates[0]["unit"]=="mSv/day"

def test_manual_checkin_validation(client,seeded):
    source=next(x for x in seeded["sessions"] if x["source_format"]=="canonical_v1")
    astronaut=source["astronaut_id"]; mission=seeded["mission_id"]; now="2026-11-14T12:00:00Z"
    body={"astronaut_id":astronaut,"mission_id":mission,"mission_day":1,"observed_at":now,"synthetic":True,"report_kind":"user_demo","submitted_at":now,"reporting_window":{"start":"2026-11-13T12:00:00Z","end":now},"sleep_hours":8,"fatigue":{"value":8,"scale":"samn_perelli_1_7","source_scale_label":"Samn-Perelli","assessed_at":now},"legacy_fatigue":None,"hydration_intake_ml":2000,"notes":""}
    headers={"Idempotency-Key":str(uuid.uuid4())}
    assert client.post(f"/checkins?source_session_id={source['source_session_id']}",json=body,headers=headers).status_code==422
    body["fatigue"]["value"]=7; response=client.post(f"/checkins?source_session_id={source['source_session_id']}",json=body,headers=headers)
    assert response.status_code==201, response.text
    assert response.json()["item"]["fatigue"]["value"]==7
    assert client.get(f"/checkins?mission_id={mission}&astronaut_id={astronaut}&report_kind=user_demo").json()["items"]

def test_radiation_rate_cannot_be_daily_dose(client,seeded):
    s=next(x for x in seeded["sessions"] if x["source_format"]=="canonical_v1"); now="2026-11-14T12:00:00Z"
    body={"astronaut_id":s["astronaut_id"],"mission_id":seeded["mission_id"],"mission_day":1,"observed_at":now,"synthetic":True,"quantity":"daily_exposure_dose_msv","value":.5,"unit":"mSv/day","dose_basis":"unspecified","quality":"unverified","integration_window":{"start":"2026-11-13T12:00:00Z","end":now},"method":"source_reported","source_paths":["x"]}
    assert client.post(f"/radiation?source_session_id={s['source_session_id']}",json=body,headers={"Idempotency-Key":str(uuid.uuid4())}).status_code==422

def test_canonical_daily_radiation_persists(client,seeded):
    s=next(x for x in seeded["sessions"] if x["source_format"]=="canonical_v1"); now="2026-11-14T12:00:00Z"
    body={"astronaut_id":s["astronaut_id"],"mission_id":seeded["mission_id"],"mission_day":1,"observed_at":now,"synthetic":True,"quantity":"daily_exposure_dose_msv","value":0.5,"unit":"mSv","dose_basis":"unspecified","quality":"unverified","integration_window":{"start":"2026-11-13T12:00:00Z","end":now},"method":"source_reported","source_paths":["demo.explicit-24-hour-period"]}
    result=client.post(f"/radiation?source_session_id={s['source_session_id']}",json=body,headers={"Idempotency-Key":str(uuid.uuid4())})
    assert result.status_code==201,result.text
    items=client.get(f"/radiation?mission_id={seeded['mission_id']}&astronaut_id={s['astronaut_id']}").json()["items"]
    assert items[0]["quantity"]=="daily_exposure_dose_msv" and items[0]["unit"]=="mSv"

def test_persists_after_app_client_restart(client,seeded,packet):
    s=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    client.post(f"/ingest/simulator?source_session_id={s['source_session_id']}",json=packet)
    with client.__class__(client.app) as restarted:
        assert restarted.get(f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={s['astronaut_id']}").json()["items"]

def test_historical_filter(client,seeded,packet):
    s=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    client.post(f"/ingest/simulator?source_session_id={s['source_session_id']}",json=packet)
    base=f"mission_id={seeded['mission_id']}&astronaut_id={s['astronaut_id']}"
    assert len(client.get(f"/measurements?{base}&from=2026-11-14T14:00:00Z&to=2026-11-14T15:00:00Z").json()["items"])==1
    assert client.get(f"/measurements?{base}&from=2026-11-15T14:00:00Z&to=2026-11-16T14:00:00Z").json()["items"]==[]

def test_cursor_paginates_and_binds_filters(client,seeded,packet):
    session=next(x for x in seeded["sessions"] if x["source_format"]=="amina_simulator_v1")
    url=f"/ingest/simulator?source_session_id={session['source_session_id']}"
    assert client.post(url,json=packet).status_code==201
    second=json.loads(json.dumps(packet)); second["simulator"]["sequence"]=2
    second["ingestion_payload_contract"]["ingestion_context"]["payload_id"]+="-2"
    second["ingestion_payload_contract"]["ingestion_context"]["timestamp_utc"]="2026-11-14T14:31:00Z"
    second["simulator"]["sent_at"]="2026-11-14T14:31:00Z"
    assert client.post(url,json=second).status_code==201
    base=f"/measurements?mission_id={seeded['mission_id']}&astronaut_id={session['astronaut_id']}&limit=1"
    first=client.get(base).json(); assert len(first["items"])==1 and first["next_cursor"]
    next_page=client.get(base+"&cursor="+first["next_cursor"]).json()
    assert len(next_page["items"])==1 and next_page["next_cursor"] is None
    assert client.get(base+"&cursor="+first["next_cursor"]+"&from=2026-11-01T00:00:00Z").status_code==422
