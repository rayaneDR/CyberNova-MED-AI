import json, os, uuid, hashlib, logging
import base64
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from .db import get_db, initialize_database
from . import models
from .service import dump, iso, parse, session_for, persist_ingest, utcnow
from .analytics_adapter import materialize_analytics
from .docs_contract_import import *  # noqa: F403
from .response_models import (  # noqa: E402
    AlertEnvelope, AlertsList, AnalyticsSummary, AstronautList, CheckIn,
    CheckInList, HealthResponse, ItemOnly, ItemResponse, MeasurementList, RadiationList,
    RadiationReading, Receipt,
)

logger=logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app):
    initialize_database()
    yield

app=FastAPI(title="CyberNova MED-AI API",version="1.0.0",description="Synthetic-only astronaut health monitoring MVP. No diagnoses or treatment advice.",lifespan=lifespan)
origin=os.getenv("FRONTEND_ORIGIN","http://localhost:3000")
app.add_middleware(CORSMiddleware,allow_origins=[origin],allow_credentials=False,allow_methods=["GET","POST","PATCH"],allow_headers=["Authorization","Content-Type","Idempotency-Key"])

def auth_write(authorization: str|None):
    token=os.getenv("WRITE_TOKEN","")
    if token and authorization!=f"Bearer {token}": raise HTTPException(401,"Authentication required")
    if not token and os.getenv("ALLOW_NON_LOOPBACK","false").lower()=="true": raise HTTPException(503,"WRITE_TOKEN is required for non-loopback binding")

def body_json(request_body):
    try: return parse(request_body.decode("utf-8"))
    except (UnicodeDecodeError,ValueError) as e: raise HTTPException(400,detail={"error":{"code":"INVALID_JSON","message":str(e),"details":[]}})

def err(e):
    if isinstance(e,SQLAlchemyError): return HTTPException(503,detail={"error":{"code":"STORAGE_UNAVAILABLE","message":"Persistence is temporarily unavailable","details":[]}})
    if isinstance(e,LookupError): return HTTPException(422,detail={"error":{"code":"UNRESOLVED_IDENTITY","message":str(e),"details":[]}})
    if isinstance(e,FileExistsError): return HTTPException(409,detail={"error":{"code":"IDEMPOTENCY_CONFLICT","message":str(e),"details":[]}})
    if isinstance(e,OverflowError): return HTTPException(413,detail={"error":{"code":"BODY_TOO_LARGE","message":str(e),"details":[]}})
    return HTTPException(422,detail={"error":{"code":"VALIDATION_ERROR","message":str(e),"details":[]}})

def check_json(model, data):
    try: return model.model_validate_json(dump(data)).model_dump(mode="json")
    except ValidationError as e: raise HTTPException(422,detail={"error":{"code":"VALIDATION_ERROR","message":"Request does not match contract","details":jsonable_encoder(e.errors(include_url=False))}})

def response_model(model, data):
    # Validate from JSON so strict UUID and aware-datetime fields accept their wire representation.
    return model.model_validate_json(dump(data))

@app.get("/health",response_model=HealthResponse)
def health(db:Session=Depends(get_db)):
    try: db.execute(select(1)); return {"status":"ok","contract_version":"1.0.0","storage":"ready","analytics":"ready","synthetic_only":True}
    except Exception: raise HTTPException(503,{"status":"unavailable","contract_version":"1.0.0","storage":"unavailable","analytics":"ready","synthetic_only":True})

@app.get("/astronauts",response_model=AstronautList)
def astronauts(mission_id:uuid.UUID,db:Session=Depends(get_db)):
    rows=db.scalars(select(models.AstronautRow).where(models.AstronautRow.mission_id==str(mission_id)).order_by(models.AstronautRow.id)).all()
    out=[]
    for a in rows:
        aliases=db.scalars(select(models.AliasRow).where(models.AliasRow.astronaut_id==a.id)).all()
        out.append({"id":a.id,"mission_id":a.mission_id,"display_name":a.display_name,"role":a.role,"aliases":[{"namespace":x.namespace,"value":x.value} for x in aliases],"synthetic":True})
    return response_model(AstronautList,{"items":out,"next_cursor":None,"synthetic":True})

def page(db,kind,mission_id,astronaut_id,from_,to,limit,quantity=None,report_kind=None,fatigue_scale=None,cursor=None):
    filters={"kind":kind,"mission_id":str(mission_id),"astronaut_id":str(astronaut_id),"from":iso(from_) if from_ else None,"to":iso(to) if to else None,"quantity":quantity,"report_kind":report_kind,"fatigue_scale":fatigue_scale}
    q=select(models.ResourceRow,models.IngestRow.received_at).join(models.IngestRow,models.ResourceRow.ingest_id==models.IngestRow.id).where(models.ResourceRow.kind==kind,models.ResourceRow.mission_id==str(mission_id),models.ResourceRow.astronaut_id==str(astronaut_id))
    if from_: q=q.where(models.ResourceRow.event_at>=iso(from_))
    if to: q=q.where(models.ResourceRow.event_at<iso(to))
    snapshot=utcnow(); after=None
    if cursor:
        try:
            decoded=json.loads(base64.urlsafe_b64decode(cursor+"="*(-len(cursor)%4)))
            if decoded["filters"]!=filters: raise ValueError("cursor filters differ")
            snapshot=decoded["snapshot"]; after=(decoded["event_at"],decoded["id"])
            datetime.fromisoformat(snapshot.replace("Z","+00:00"))
        except Exception: raise HTTPException(422,"Invalid or filter-mismatched cursor")
    q=q.where(models.IngestRow.received_at<=snapshot)
    pairs=db.execute(q.order_by(models.ResourceRow.event_at,models.ResourceRow.id)).all()
    items=[]
    for row,received_at in pairs:
        if after and (row.event_at,row.id)<=after: continue
        item=json.loads(row.payload_json)
        if quantity and item.get("quantity")!=quantity: continue
        if quantity is None and kind=="radiation" and item.get("quantity") not in ("daily_exposure_dose_msv","cumulative_mission_dose_msv"): continue
        if report_kind and item.get("report_kind")!=report_kind: continue
        if fatigue_scale and kind=="checkin" and fatigue_scale not in ((item.get("fatigue") or {}).get("scale"),(item.get("legacy_fatigue") or {}).get("scale")): continue
        items.append(item)
    more=len(items)>limit; items=items[:limit]; next_cursor=None
    if more and items:
        last=items[-1]; next_cursor=base64.urlsafe_b64encode(json.dumps({"filters":filters,"snapshot":snapshot,"event_at":last.get("observed_at"),"id":last["id"]},separators=(",",":")).encode()).decode().rstrip("=")
    return items,next_cursor

def common_params(mission_id,astronaut_id,from_,to,limit):
    if from_ and to and from_>=to: raise HTTPException(422,"from must be earlier than to")

@app.get("/measurements",response_model=MeasurementList)
def measurements(mission_id:uuid.UUID,astronaut_id:uuid.UUID,from_:datetime|None=Query(None,alias="from"),to:datetime|None=None,limit:Annotated[int,Query(ge=1,le=500)]=100,cursor:str|None=None,db:Session=Depends(get_db)):
    common_params(mission_id,astronaut_id,from_,to,limit); items,next_cursor=page(db,"measurement",mission_id,astronaut_id,from_,to,limit,cursor=cursor)
    ids=[x["id"] for x in items]; health=[json.loads(h.payload_json) for h in db.scalars(select(models.SensorHealthRow).where(models.SensorHealthRow.measurement_id.in_(ids))).all()] if ids else []
    return response_model(MeasurementList,{"items":items,"next_cursor":next_cursor,"synthetic":True,"sensor_health":health})

def canonical_write(db,source_session_id,fmt,model,data,key,authorization):
    auth_write(authorization); s=session_for(db,str(source_session_id),fmt)
    if not key: raise HTTPException(422,"Idempotency-Key UUID is required")
    try: uuid.UUID(key)
    except ValueError: raise HTTPException(422,"Idempotency-Key must be a UUID")
    body=check_json(model,data); raw=dump(data); sha=hashlib.sha256(raw.encode()).hexdigest(); sid=body["astronaut_id"]
    astro=db.get(models.AstronautRow,sid)
    if not astro or astro.mission_id!=str(body["mission_id"]) or astro.mission_id!=s.mission_id: raise HTTPException(422,"Astronaut, mission, and source session must match")
    if "quantity" in body and body["quantity"]=="cumulative_mission_dose_msv":
        mission=db.get(models.MissionRow,astro.mission_id)
        if body["integration_window"]["start"]!=iso(mission.start_at): raise HTTPException(422,"Cumulative mission window must begin at the registered mission start")
    existing=db.scalar(select(models.IngestRow).where(models.IngestRow.source_session_id==s.id,models.IngestRow.source_record_id==key))
    if existing:
        if existing.payload_sha256!=sha: raise HTTPException(409,"Idempotency-Key reused with different body")
        old=json.loads(existing.receipt_json)
        if old["measurement_ids"]: old["duplicate"]=True; return old,True
        resource_id=(old["checkin_ids"] or old["radiation_ids"])[0]
        resource=db.get(models.ResourceRow,resource_id)
        return {"item":json.loads(resource.payload_json),"duplicate":True},True
    now=utcnow(); iid=str(uuid.uuid4()); rid=str(uuid.uuid4()); prov={"source_format":fmt,"source_session_id":s.id,"source_record_id":key,"source_sent_at":None,"received_at":now,"ingest_id":iid,"payload_sha256":sha}; event=body.get("observed_at") or body.get("submitted_at")
    item={**body,"id":rid,"provenance":prov}
    receipt={"ingest_id":iid,"duplicate":False,"synthetic":True,"measurement_ids":[rid] if isinstance(body,dict) and "heart_rate_bpm" in body else [],"checkin_ids":[rid] if isinstance(body,dict) and "report_kind" in body else [],"radiation_ids":[rid] if isinstance(body,dict) and "quantity" in body else [],"warnings":[]}
    ingest=models.IngestRow(id=iid,source_session_id=s.id,source_record_id=key,payload_sha256=sha,raw_body=raw,receipt_json=dump(receipt),received_at=now); db.add(ingest)
    kind="measurement" if receipt["measurement_ids"] else "checkin" if receipt["checkin_ids"] else "radiation"
    db.add(models.ResourceRow(id=rid,kind=kind,mission_id=astro.mission_id,astronaut_id=astro.id,event_at=iso(event),ingest_id=iid,payload_json=dump(item)))
    try:
        if kind == "measurement":
            for channel in ("heart_rate_bpm", "spo2_percent", "respiratory_rate_per_min"):
                reading=item[channel]
                issue_code={"missing":"VALUE_MISSING","invalid":"INVALID_VALUE","conflict":"ALIAS_CONFLICT"}.get(reading["quality"])
                health_item={"id":str(uuid.uuid4()),"measurement_id":rid,"channel":channel,"source_reported_status":None,"hardware_model_claim":None,"quality":reading["quality"],"issue_codes":[issue_code] if issue_code else [],"connectivity":"unknown","last_source_sample_at":iso(item["observed_at"]),"last_non_null_sample_at":iso(item["observed_at"]) if reading["value"] is not None else None,"synthetic":True}
                db.add(models.SensorHealthRow(id=health_item["id"],measurement_id=rid,payload_json=dump(health_item)))
        db.commit()
    except SQLAlchemyError as e:
        db.rollback(); raise err(e)
    return {"item":item,"duplicate":False} if kind!="measurement" else receipt,False

@app.post("/measurements",status_code=201,response_model=Receipt)
async def post_measurements(request:Request,source_session_id:uuid.UUID,input_format:str=Query(...),idempotency_key:str|None=Header(None,alias="Idempotency-Key"),authorization:str|None=Header(None),db:Session=Depends(get_db)):
    raw=(await request.body())
    if len(raw)>1048576: raise HTTPException(413,"Request body exceeds 1 MiB")
    data=body_json(raw)
    if input_format=="ayoub_raw_v1":
        auth_write(authorization); s=session_for(db,str(source_session_id),input_format)
        try: receipt,created=persist_ingest(db,s,data,raw.decode(),input_format)
        except Exception as e: db.rollback(); raise err(e)
        return JSONResponse(status_code=201 if created else 200,content=receipt)
    if input_format!="canonical_v1": raise HTTPException(422,"Unsupported input_format")
    # Canonical write uses the same envelope receipt and source idempotency semantics.
    auth_write(authorization); s=session_for(db,str(source_session_id),input_format)
    if not idempotency_key: raise HTTPException(422,"Idempotency-Key UUID is required")
    try: uuid.UUID(idempotency_key); item=check_json(MeasurementInput,data)
    except (ValueError,ValidationError) as e: raise err(e)
    result,duplicate=canonical_write(db,source_session_id,input_format,MeasurementInput,data,idempotency_key,authorization)
    return JSONResponse(status_code=200 if duplicate else 201,content=result)

from fastapi.responses import JSONResponse

@app.post("/ingest/simulator",status_code=201,response_model=Receipt)
async def ingest_simulator(request:Request,source_session_id:uuid.UUID,authorization:str|None=Header(None),db:Session=Depends(get_db)):
    auth_write(authorization); raw=await request.body()
    if len(raw)>1048576: raise HTTPException(413,"Request body exceeds 1 MiB")
    data=body_json(raw)
    try:
        s=session_for(db,str(source_session_id),"amina_simulator_v1"); receipt,created=persist_ingest(db,s,data,raw.decode(),"amina_simulator_v1")
        return JSONResponse(status_code=201 if created else 200,content=receipt)
    except Exception as e: db.rollback(); raise err(e)

def post_resource(kind,model,fmt):
    async def route(request:Request,source_session_id:uuid.UUID,idempotency_key:str|None=Header(None,alias="Idempotency-Key"),authorization:str|None=Header(None),db:Session=Depends(get_db)):
        auth_write(authorization); raw=await request.body()
        if len(raw)>1048576: raise HTTPException(413,"Request body exceeds 1 MiB")
        data=body_json(raw)
        try: key=str(uuid.UUID(idempotency_key)) if idempotency_key else None
        except ValueError: key=None
        if not key: raise HTTPException(422,"Idempotency-Key UUID is required")
        result,duplicate=canonical_write(db,source_session_id,fmt,model,data,key,authorization)
        return JSONResponse(status_code=200 if duplicate else 201,content=result)
    return route

app.post("/checkins",status_code=201,response_model=ItemResponse[CheckIn])(post_resource("checkin",CheckInInput,"canonical_v1"))
app.post("/radiation",status_code=201,response_model=ItemResponse[RadiationReading])(post_resource("radiation",RadiationInput,"canonical_v1"))

@app.get("/checkins",response_model=CheckInList)
def checkins(mission_id:uuid.UUID,astronaut_id:uuid.UUID,report_kind:str|None=None,fatigue_scale:str|None=None,from_:datetime|None=Query(None,alias="from"),to:datetime|None=None,limit:Annotated[int,Query(ge=1,le=500)]=100,cursor:str|None=None,db:Session=Depends(get_db)):
    common_params(mission_id,astronaut_id,from_,to,limit); items,next_cursor=page(db,"checkin",mission_id,astronaut_id,from_,to,limit,report_kind=report_kind,fatigue_scale=fatigue_scale,cursor=cursor)
    return response_model(CheckInList,{"items":items,"next_cursor":next_cursor,"synthetic":True})

@app.get("/radiation",response_model=RadiationList)
def radiation(mission_id:uuid.UUID,astronaut_id:uuid.UUID,quantity:str|None=None,from_:datetime|None=Query(None,alias="from"),to:datetime|None=None,limit:Annotated[int,Query(ge=1,le=500)]=100,cursor:str|None=None,db:Session=Depends(get_db)):
    common_params(mission_id,astronaut_id,from_,to,limit)
    if quantity and quantity not in {"daily_exposure_dose_msv","cumulative_mission_dose_msv","source_dose_rate_msv_day","source_interval_dose_msv","source_cumulative_dose_msv"}: raise HTTPException(422,"Unknown radiation quantity")
    items,next_cursor=page(db,"radiation",mission_id,astronaut_id,from_,to,limit,quantity=quantity,cursor=cursor)
    return response_model(RadiationList,{"items":items,"next_cursor":next_cursor,"synthetic":True})

@app.get("/analytics/summary",response_model=AnalyticsSummary)
def analytics_summary(mission_id:uuid.UUID,astronaut_id:uuid.UUID,db:Session=Depends(get_db)):
    try:
        result=materialize_analytics(db,str(mission_id),str(astronaut_id))
        return response_model(AnalyticsSummary,{"mission_id":str(mission_id),**result})
    except Exception as e:
        db.rollback(); logger.exception("Analytics summary failed for mission=%s astronaut=%s",mission_id,astronaut_id)
        if isinstance(e,SQLAlchemyError): raise HTTPException(503,detail={"error":{"code":"ANALYTICS_STORAGE_UNAVAILABLE","message":"Analytics persistence is temporarily unavailable"}})
        raise HTTPException(503,detail={"error":{"code":"ANALYTICS_UNAVAILABLE","message":"Analytics processing failed; no result was fabricated"}})

def _alert_items(db:Session,mission_id:str,astronaut_id:str):
    rows=db.scalars(select(models.ResourceRow).where(models.ResourceRow.kind=="measurement",models.ResourceRow.mission_id==mission_id,models.ResourceRow.astronaut_id==astronaut_id)).all(); items=[]
    for row in rows:
        for hrow in db.scalars(select(models.SensorHealthRow).where(models.SensorHealthRow.measurement_id==row.id)).all():
            h=json.loads(hrow.payload_json)
            if not h["issue_codes"] or h["quality"]=="unverified": continue
            alert_id=str(uuid.uuid5(uuid.NAMESPACE_URL,f"{row.id}:{h['channel']}:{h['issue_codes'][0]}")); ack=db.get(models.AckRow,alert_id)
            items.append({"id":alert_id,"astronaut_id":row.astronaut_id,"mission_id":row.mission_id,"detected_at":row.event_at,"kind":"sensor_data_issue","synthetic":True,"sensor_health":h,"statistical_observation":None,"acknowledgment":{"actor_id":ack.actor_id,"acknowledged_at":ack.acknowledged_at,"note":ack.note} if ack else None})
    stat_rows=db.scalars(select(models.StatisticalObservationRow).where(models.StatisticalObservationRow.mission_id==mission_id,models.StatisticalObservationRow.astronaut_id==astronaut_id,models.StatisticalObservationRow.is_active.is_(True))).all()
    for row in stat_rows:
        ack=db.get(models.AckRow,row.id)
        items.append({"id":row.id,"astronaut_id":astronaut_id,"mission_id":mission_id,"detected_at":row.detected_at,"kind":"statistical_observation","synthetic":True,"sensor_health":None,"statistical_observation":json.loads(row.payload_json),"acknowledgment":{"actor_id":ack.actor_id,"acknowledged_at":ack.acknowledged_at,"note":ack.note} if ack else None})
    return sorted(items,key=lambda item:(item["detected_at"],item["id"]))

@app.get("/alerts",response_model=AlertsList)
def alerts(mission_id:uuid.UUID,astronaut_id:uuid.UUID,kind:str|None=None,acknowledged:bool|None=None,db:Session=Depends(get_db)):
    try:
        analytics=materialize_analytics(db,str(mission_id),str(astronaut_id))
        items=_alert_items(db,str(mission_id),str(astronaut_id))
        if kind: items=[item for item in items if item["kind"]==kind]
        if acknowledged is not None: items=[item for item in items if (item["acknowledgment"] is not None)==acknowledged]
        return response_model(AlertsList,{"items":items,"next_cursor":None,"synthetic":True,"analytics_status":"ready","baseline_status":analytics["baseline_status"]})
    except Exception as e:
        db.rollback(); logger.exception("Alert listing failed for mission=%s astronaut=%s",mission_id,astronaut_id)
        if isinstance(e,SQLAlchemyError): raise HTTPException(503,detail={"error":{"code":"ANALYTICS_STORAGE_UNAVAILABLE","message":"Analytics persistence is temporarily unavailable"}})
        raise HTTPException(503,detail={"error":{"code":"ANALYTICS_UNAVAILABLE","message":"Analytics processing failed; no result was fabricated"}})

@app.patch("/alerts/{alert_id}/acknowledge",response_model=ItemOnly[AlertEnvelope])
def acknowledge(alert_id:uuid.UUID,data:AcknowledgeInput,authorization:str|None=Header(None),db:Session=Depends(get_db)):
    auth_write(authorization)
    # Only an alert deterministically derived from a stored sensor issue can be acknowledged.
    candidates=alerts_for_ack(db)
    item=next((x for x in candidates if x["id"]==str(alert_id)),None)
    if not item: raise HTTPException(404,"Alert not found")
    ack=db.get(models.AckRow,str(alert_id))
    if not ack:
        actor=os.getenv("ACK_ACTOR_ID","local-operator"); ack=models.AckRow(alert_id=str(alert_id),actor_id=actor,acknowledged_at=utcnow(),note=data.note); db.add(ack); db.commit()
    item["acknowledgment"]={"actor_id":ack.actor_id,"acknowledged_at":ack.acknowledged_at,"note":ack.note}
    return response_model(ItemOnly[AlertEnvelope],{"item":item})

def alerts_for_ack(db):
    result=[]
    for astronaut in db.scalars(select(models.AstronautRow)).all():
        materialize_analytics(db,astronaut.mission_id,astronaut.id)
        result.extend(_alert_items(db,astronaut.mission_id,astronaut.id))
    return result
