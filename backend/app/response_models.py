"""Explicit FastAPI response models shared with the reviewed v1 contract."""
import sys
from pathlib import Path
from typing import Generic, Literal, TypeVar
from pydantic import BaseModel, ConfigDict

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from docs.contracts.v1_design import (  # noqa: E402
    Astronaut, CheckIn, Measurement, RadiationReading, SensorHealth,
    StatisticalObservation,
)

T=TypeVar("T")

class ResponseModel(BaseModel):
    model_config=ConfigDict(extra="forbid", strict=True)

class ListResponse(ResponseModel,Generic[T]):
    items:list[T]
    next_cursor:str|None
    synthetic:Literal[True]

class AstronautList(ListResponse[Astronaut]): pass

class MeasurementList(ListResponse[Measurement]):
    sensor_health:list[SensorHealth]

class CheckInList(ListResponse[CheckIn]): pass

class RadiationList(ListResponse[RadiationReading]): pass

class AlertAcknowledgment(ResponseModel):
    actor_id:str
    acknowledged_at:str
    note:str

class AlertEnvelope(ResponseModel):
    id:str
    astronaut_id:str
    mission_id:str
    detected_at:str
    kind:Literal["sensor_data_issue","statistical_observation"]
    synthetic:Literal[True]
    sensor_health:SensorHealth|None
    statistical_observation:StatisticalObservation|None
    acknowledgment:AlertAcknowledgment|None

class AlertsList(ListResponse[AlertEnvelope]):
    analytics_status:Literal["ready"]
    baseline_status:Literal["ready","insufficient_baseline"]

class Receipt(ResponseModel):
    ingest_id:str
    duplicate:bool
    synthetic:Literal[True]
    measurement_ids:list[str]
    checkin_ids:list[str]
    radiation_ids:list[str]
    warnings:list[dict[str,str]]

class ItemResponse(ResponseModel,Generic[T]):
    item:T
    duplicate:bool

class ItemOnly(ResponseModel,Generic[T]):
    item:T

class HealthResponse(ResponseModel):
    status:Literal["ok","unavailable"]
    contract_version:Literal["1.0.0"]
    storage:Literal["ready","unavailable"]
    analytics:Literal["ready"]
    synthetic_only:Literal[True]

class MetricBaselineSummary(ResponseModel):
    astronaut_id:str
    metric:Literal["heart_rate_bpm","spo2_percent","respiratory_rate_per_min"]
    activity_context:Literal["RESTING","SLEEP","EXERCISE","EVA_PREP","EVA_ACTIVE","LAB_WORK","UNKNOWN"]
    status:Literal["READY","INSUFFICIENT_BASELINE"]
    valid_measurement_count:int
    baseline_sample_count:int
    baseline_median:float|None
    mad:float|None

class AnalyticsConfiguration(ResponseModel):
    history_window:int
    minimum_baseline:int
    robust_z_threshold:float
    baseline_guard_z:float
    ewma_alpha:float
    ewma_z_threshold:float
    required_consecutive:int
    dispersion_floors:dict[str,float]

class AnalyticsSummary(ResponseModel):
    astronaut_id:str
    mission_id:str
    analytics_status:Literal["ready"]
    baseline_status:Literal["ready","insufficient_baseline"]
    statistical_observations_count:int
    latest_measurement_at:str|None
    algorithm_version:str
    configuration:AnalyticsConfiguration
    metrics:list[MetricBaselineSummary]
    synthetic:Literal[True]
