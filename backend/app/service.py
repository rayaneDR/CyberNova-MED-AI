import hashlib, json
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import AliasRow, AstronautRow, IngestRow, ResourceRow, SensorHealthRow, SourceSessionRow

def utcnow(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def iso(value):
    if isinstance(value, datetime): value=value.isoformat()
    parsed=datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None: raise ValueError("Timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
def dump(value): return json.dumps(value, separators=(",",":"), ensure_ascii=False, allow_nan=False)
def parse(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise ValueError("Duplicate JSON object key")
            out[k]=v
        return out
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))

def session_for(db: Session, session_id: str, expected: str | None = None):
    s=db.get(SourceSessionRow, session_id)
    if not s: raise LookupError("Unknown source_session_id; register it with the seed CLI")
    if expected and s.source_format != expected: raise ValueError("Input format does not match source session")
    return s

def identity(db, session, external_id):
    aliases=json.loads(session.allowed_aliases_json)
    if external_id not in aliases: raise LookupError(f"Unresolved alias {external_id!r} for source session")
    row=db.scalar(select(AliasRow).where(AliasRow.mission_id==session.mission_id, AliasRow.namespace==session.namespace, AliasRow.value==external_id))
    if not row: raise LookupError("Alias binding is missing")
    return db.get(AstronautRow,row.astronaut_id)

def provenance(fmt, session, record_id, sent, received, ingest_id, sha):
    return {"source_format":fmt,"source_session_id":session.id,"source_record_id":record_id,"source_sent_at":iso(sent) if sent else None,"received_at":received,"ingest_id":ingest_id,"payload_sha256":sha}

def _reading(value, unit, path, *, alias=None, status=None):
    paths=[path]+([alias[0]] if alias else [])
    if alias and value != alias[1]: return {"value":None,"unit":unit,"quality":"conflict","source_paths":paths},"ALIAS_CONFLICT"
    if value is None: return {"value":None,"unit":unit,"quality":"missing","source_paths":paths},"VALUE_MISSING"
    if isinstance(value,bool) or not isinstance(value,(int,float)): return {"value":None,"unit":unit,"quality":"invalid","source_paths":paths},"INVALID_VALUE"
    if unit=="percent" and not 0<=value<=100: return {"value":None,"unit":unit,"quality":"invalid","source_paths":paths},"INVALID_VALUE"
    if value<0: return {"value":None,"unit":unit,"quality":"invalid","source_paths":paths},"INVALID_VALUE"
    return {"value":value,"unit":unit,"quality":"unverified","source_paths":paths},None

def build_packet(db, session, body, raw, fmt):
    received=utcnow(); sha=hashlib.sha256(raw.encode()).hexdigest(); ingest_id=str(uuid4()); warnings=[]
    if fmt=="amina_simulator_v1":
        sim=body.get("simulator",{}); root=body.get("ingestion_payload_contract",{}); ctx=root.get("ingestion_context",{}); sensors=root.get("telemetry_sensors",{}); rad=root.get("radiation_dosimetry_sensors",{})
        external=ctx.get("astronaut_id"); record=ctx.get("payload_id"); sent=sim.get("sent_at")
        seq=sim.get("sequence"); ramp=sim.get("anomaly_ramp")
        if body.get("project") is None or sim.get("mode") not in ("normal","anomaly","failure") or not record: raise ValueError("Malformed simulator envelope")
        if isinstance(seq,bool) or not isinstance(seq,int) or not 1<=seq<2**63: raise ValueError("Simulator sequence must be a positive signed 64-bit integer")
        if isinstance(ramp,bool) or not isinstance(ramp,(int,float)) or not 0<=ramp<=1: raise ValueError("anomaly_ramp must be between 0 and 1")
        day=ctx.get("mission_day")
        if isinstance(day,bool) or not isinstance(day,int) or day<1: raise ValueError("mission_day must be a positive integer")
        observed=iso(ctx.get("timestamp_utc")); activity=ctx.get("activity_context") or "UNKNOWN"
        if activity not in ("RESTING","SLEEP","EXERCISE","EVA_PREP","EVA_ACTIVE","LAB_WORK","UNKNOWN"): activity="UNKNOWN"
        channels=[]
        channel_specs=[("heart_rate_bpm","heart_rate_bpm","bpm",None), ("spo2_percent","spo2_percent","percent","spo2"),("respiratory_rate_per_min","respiratory_rate_rpm","breaths/min","respiratory_rate")]
        for canonical,key,unit,alias_key in channel_specs:
            node=sensors.get(key)
            if not isinstance(node,dict) or not isinstance(node.get("unit"),str): raise ValueError(f"Missing required unit for {key}")
            expected={"heart_rate_bpm":"bpm","spo2_percent":"%","respiratory_rate_rpm":"rpm"}[key]
            if node["unit"]!=expected: raise ValueError(f"Unexpected unit for {key}: {node['unit']}")
            alias=(f"telemetry_sensors.{key}.{alias_key}",node.get(alias_key)) if alias_key and alias_key in node else None
            reading,issue=_reading(node.get("value"),unit,f"telemetry_sensors.{key}.value",alias=alias)
            channels.append((canonical,reading,node,issue))
        warnings.extend({"code":issue,"path":r["source_paths"][0],"message":"Source channel is missing, invalid, or has conflicting aliases; raw packet retained"} for _,r,_,issue in channels if issue)
        astronaut=identity(db,session,external)
        measurement={"astronaut_id":astronaut.id,"mission_id":session.mission_id,"mission_day":ctx.get("mission_day"),"observed_at":observed,"synthetic":True,"activity_context":activity}
        health=[]
        for canonical,r,node,issue in channels:
            measurement[canonical]=r
            health.append({"id":str(uuid4()),"measurement_id":None,"channel":canonical,"source_reported_status":None,"hardware_model_claim":None,"quality":r["quality"],"issue_codes":[issue or "STATUS_UNREPORTED"],"connectivity":"unknown","last_source_sample_at":observed,"last_non_null_sample_at":observed if r["value"] is not None else None,"synthetic":True})
        checkins=[]; radiation=[]
        manual=root.get("manual_checkin") or {}
        if manual:
            fatigue=manual.get("fatigue_score_1_10")
            checkins.append({"astronaut_id":astronaut.id,"mission_id":session.mission_id,"mission_day":ctx.get("mission_day"),"observed_at":observed,"synthetic":True,"report_kind":"simulator_snapshot","submitted_at":None,"reporting_window":None,"sleep_hours":manual.get("sleep_duration_hours"),"fatigue":None,"legacy_fatigue":{"value":fatigue,"scale":"source_ordinal_1_10","source_scale_label":"fatigue_score_1_10","source_path":"manual_checkin.fatigue_score_1_10"} if isinstance(fatigue,int) and not isinstance(fatigue,bool) and 1<=fatigue<=10 else None,"hydration_intake_ml":manual.get("hydration_intake_ml_24h"),"notes":"Synthetic simulator snapshot; not a user-submitted check-in."})
            if fatigue is not None: warnings.append({"code":"LEGACY_FATIGUE_SCALE","path":"manual_checkin.fatigue_score_1_10","message":"Retained as 1–10; canonical fatigue is unavailable"})
        rate=rad.get("dose_equivalent_rate_msv_day")
        cumulative=rad.get("cumulative_mission_dose_msv")
        for quantity,value,unit,path,window in [("source_dose_rate_msv_day",rate,"mSv/day","radiation_dosimetry_sensors.dose_equivalent_rate_msv_day",None),("source_cumulative_dose_msv",cumulative,"mSv","radiation_dosimetry_sensors.cumulative_mission_dose_msv",None)]:
            if value is None: continue
            if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0: quality="invalid"; value_out=None
            else: quality="unverified"; value_out=value
            radiation.append({"astronaut_id":astronaut.id,"mission_id":session.mission_id,"mission_day":ctx.get("mission_day"),"observed_at":observed,"synthetic":True,"quantity":quantity,"value":value_out,"unit":unit,"dose_basis":"dose_equivalent" if quantity=="source_dose_rate_msv_day" else "unspecified","quality":quality,"integration_window":window,"method":"source_reported","source_paths":[path]})
        if radiation: warnings.append({"code":"RADIATION_PERIOD_UNCONFIRMED","path":"radiation_dosimetry_sensors","message":"Rate and cumulative source values are not completed canonical daily/mission doses"})
        record_id=record; source_sent=sent
        extra={"activity_context":activity,"simulator_mode":sim["mode"],"scenario":sim.get("scenario"),"sequence":seq,"anomaly_ramp":ramp}
        fmt="amina_simulator_v1"
    elif fmt=="ayoub_raw_v1":
        external=body.get("astronaut_id"); record_id=body.get("record_id"); source_sent=None
        if not external or not record_id: raise ValueError("Missing astronaut_id or record_id")
        astronaut=identity(db,session,external); observed=iso(body.get("timestamp_utc")); activity=body.get("activity_context","UNKNOWN")
        src=body.get("automated_sensors",{}); channels=[]
        for canonical,key,unit in [("heart_rate_bpm","heart_rate","bpm"),("spo2_percent","spo2","percent"),("respiratory_rate_per_min","respiratory_rate","breaths/min")]:
            n=src.get(key,{})
            expected_unit={"heart_rate":"bpm","spo2":"percent","respiratory_rate":"breaths_per_min"}[key]
            if n.get("unit")!=expected_unit: raise ValueError(f"Unexpected unit for {key}")
            r,issue=_reading(n.get("value"),unit,f"automated_sensors.{key}.value")
            channels.append((canonical,r,n,issue))
        measurement={"astronaut_id":astronaut.id,"mission_id":session.mission_id,"mission_day":body.get("mission_day"),"observed_at":observed,"synthetic":True,"activity_context":activity}
        health=[]
        for canonical,r,n,issue in channels:
            measurement[canonical]=r
            status=n.get("sensor_status")
            health.append({"id":str(uuid4()),"measurement_id":None,"channel":canonical,"source_reported_status":status,"hardware_model_claim":n.get("sensor_hardware_model"),"quality":r["quality"],"issue_codes":[issue] if issue else (["SOURCE_STATUS_NOT_VALID"] if status!="VALID" else []),"connectivity":"unknown","last_source_sample_at":observed,"last_non_null_sample_at":observed if r["value"] is not None else None,"synthetic":True})
        radiation=[]; rad=body.get("radiation_dosimetry",{})
        for key,quantity,path in [("daily_exposure_dose","source_interval_dose_msv","radiation_dosimetry.daily_exposure_dose.value"),("cumulative_mission_dose","source_cumulative_dose_msv","radiation_dosimetry.cumulative_mission_dose.value")]:
            node=rad.get(key)
            if not node: continue
            val=node.get("value"); ok=isinstance(val,(int,float)) and not isinstance(val,bool) and val>=0
            radiation.append({"astronaut_id":astronaut.id,"mission_id":session.mission_id,"mission_day":body.get("mission_day"),"observed_at":observed,"synthetic":True,"quantity":quantity,"value":val if ok else None,"unit":"mSv","dose_basis":"unspecified","quality":"unverified" if ok else ("missing" if val is None else "invalid"),"integration_window":None,"method":"source_reported","source_paths":[path]})
        manual=body.get("manual_checkin",{}); checkins=[]
        fatigue=manual.get("fatigue_level",{}); fv=fatigue.get("value")
        canonical_fatigue={"value":fv,"scale":"samn_perelli_1_7","source_scale_label":fatigue.get("scale","source scale label not supplied"),"assessed_at":None} if isinstance(fv,int) and not isinstance(fv,bool) and 1<=fv<=7 else None
        checkins.append({"astronaut_id":astronaut.id,"mission_id":session.mission_id,"mission_day":body.get("mission_day"),"observed_at":observed,"synthetic":True,"report_kind":"source_snapshot","submitted_at":None,"reporting_window":None,"sleep_hours":(manual.get("sleep_duration") or {}).get("value"),"fatigue":canonical_fatigue,"legacy_fatigue":None,"hydration_intake_ml":(manual.get("hydration_intake") or {}).get("value"),"notes":"Imported source snapshot; original submitted flag is not a backend submission."})
        if radiation: warnings.append({"code":"RADIATION_PERIOD_UNCONFIRMED","path":"radiation_dosimetry","message":"Source period/origin is unknown; retained as source-only values"})
        extra={"collection_mode":body.get("collection_mode")}; fmt="ayoub_raw_v1"
    else: raise ValueError("Unsupported source format")
    prov=provenance(fmt,session,record_id,source_sent,received,ingest_id,sha)
    measurement.update({"id":str(uuid4()),"provenance":prov})
    resources=[("measurement",measurement,observed)]
    for item in checkins+radiation:
        item.update({"id":str(uuid4()),"provenance":prov}); resources.append(("checkin" if item in checkins else "radiation",item,item["observed_at"]))
    receipt={"ingest_id":ingest_id,"duplicate":False,"synthetic":True,"measurement_ids":[measurement["id"]],"checkin_ids":[r[1]["id"] for r in resources if r[0]=="checkin"],"radiation_ids":[r[1]["id"] for r in resources if r[0]=="radiation"],"warnings":warnings}
    return receipt,resources,health,record_id,sha,received,extra

def persist_ingest(db, session, body, raw, fmt):
    if len(raw.encode())>1_048_576: raise OverflowError("Request body exceeds 1 MiB")
    record_id=(body.get("ingestion_payload_contract",{}).get("ingestion_context",{}).get("payload_id") if fmt=="amina_simulator_v1" else body.get("record_id"))
    if not record_id: raise ValueError("Source record ID is required")
    sha=hashlib.sha256(raw.encode()).hexdigest()
    existing=db.scalar(select(IngestRow).where(IngestRow.source_session_id==session.id,IngestRow.source_record_id==record_id))
    if existing:
        if existing.payload_sha256!=sha: raise FileExistsError("Source record ID was already accepted with different body bytes")
        receipt=json.loads(existing.receipt_json); receipt["duplicate"]=True
        return receipt,False
    receipt,resources,health,record_id,sha,received,extra=build_packet(db,session,body,raw,fmt)
    ingest=IngestRow(id=receipt["ingest_id"],source_session_id=session.id,source_record_id=record_id,payload_sha256=sha,raw_body=raw,receipt_json=dump(receipt),received_at=received)
    db.add(ingest); db.flush()
    for kind,payload,event_at in resources:
        db.add(ResourceRow(id=payload["id"],kind=kind,mission_id=payload["mission_id"],astronaut_id=payload["astronaut_id"],event_at=event_at,ingest_id=ingest.id,payload_json=dump(payload)))
    db.flush()
    mid=receipt["measurement_ids"][0]
    for h in health:
        h["measurement_id"]=mid; db.add(SensorHealthRow(id=h["id"],measurement_id=mid,payload_json=dump(h)))
    db.commit()
    return receipt,True
