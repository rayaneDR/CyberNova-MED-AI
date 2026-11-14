"""Executable contract design only. No FastAPI service, adapters, storage, or analytics.

Uses already available Pydantic 2.14.1. Outputs JSON Schema when run directly.
"""
from datetime import timezone
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID
import json

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_serializer, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Window(Model):
    start: AwareDatetime
    end: AwareDatetime

    @model_validator(mode="after")
    def ordered(self):
        if self.end <= self.start:
            raise ValueError("Window end must be after start")
        return self

    @field_serializer("start", "end")
    def utc(self, value):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class Provenance(Model):
    source_format: Literal["ayoub_raw_v1", "amina_simulator_v1", "canonical_v1", "frontend_mock_v1"]
    source_session_id: UUID
    source_record_id: Annotated[str, Field(min_length=1, max_length=200)]
    source_sent_at: AwareDatetime | None
    received_at: AwareDatetime
    ingest_id: UUID
    payload_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]

    @field_serializer("source_sent_at", "received_at")
    def utc(self, value):
        return None if value is None else value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class Alias(Model):
    namespace: Annotated[str, Field(min_length=1, max_length=100)]
    value: Annotated[str, Field(min_length=1, max_length=100)]


class Astronaut(Model):
    id: UUID
    mission_id: UUID
    display_name: Annotated[str, Field(min_length=1, max_length=100)]
    role: Annotated[str, Field(min_length=1, max_length=100)]
    aliases: list[Alias]
    synthetic: Literal[True]


class Context(Model):
    astronaut_id: UUID
    mission_id: UUID
    mission_day: Annotated[int, Field(ge=1)] | None
    observed_at: AwareDatetime
    synthetic: Literal[True]

    @field_serializer("observed_at")
    def utc(self, value):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class Reading(Model):
    value: float | None
    unit: str
    quality: Literal["unverified", "missing", "invalid", "conflict"]
    source_paths: Annotated[list[str], Field(min_length=1)]

    @model_validator(mode="after")
    def quality_matches_value(self):
        if (self.quality == "unverified") != (self.value is not None):
            raise ValueError("Unverified readings need a value; missing/invalid/conflict readings must be null")
        return self


class HeartRate(Reading):
    value: Annotated[float, Field(ge=0)] | None
    unit: Literal["bpm"]


class Oxygen(Reading):
    value: Annotated[float, Field(ge=0, le=100)] | None
    unit: Literal["percent"]


class Breathing(Reading):
    value: Annotated[float, Field(ge=0)] | None
    unit: Literal["breaths/min"]


class MeasurementInput(Context):
    activity_context: Literal["RESTING", "SLEEP", "EXERCISE", "EVA_PREP", "EVA_ACTIVE", "LAB_WORK", "UNKNOWN"]
    heart_rate_bpm: HeartRate
    spo2_percent: Oxygen
    respiratory_rate_per_min: Breathing


class Measurement(MeasurementInput):
    id: UUID
    provenance: Provenance


class Fatigue(Model):
    value: Annotated[int, Field(ge=1, le=7)]
    scale: Literal["samn_perelli_1_7"]
    source_scale_label: str
    assessed_at: AwareDatetime | None

    @field_serializer("assessed_at")
    def utc(self, value):
        return None if value is None else value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class LegacyFatigue(Model):
    value: Annotated[int, Field(ge=1, le=10)]
    scale: Literal["source_ordinal_1_10"]
    source_scale_label: str
    source_path: str


class CheckInInput(Context):
    report_kind: Literal["user_demo", "source_snapshot", "simulator_snapshot"]
    submitted_at: AwareDatetime | None
    reporting_window: Window | None
    sleep_hours: Annotated[float, Field(ge=0, le=24)] | None
    fatigue: Fatigue | None
    legacy_fatigue: LegacyFatigue | None
    hydration_intake_ml: Annotated[float, Field(ge=0, le=10000)] | None
    notes: Annotated[str, Field(max_length=500)]

    @model_validator(mode="after")
    def user_report_requirements(self):
        if self.report_kind == "user_demo":
            if self.submitted_at is None or self.reporting_window is None:
                raise ValueError("User reports need submission time and reporting window")
            if any(value is None for value in (self.sleep_hours, self.fatigue, self.hydration_intake_ml)):
                raise ValueError("User reports require all three core fields")
            if self.legacy_fatigue is not None or self.fatigue.assessed_at is None:
                raise ValueError("User reports require a current canonical fatigue assessment, not legacy fatigue")
            if (self.reporting_window.end - self.reporting_window.start).total_seconds() != 86400:
                raise ValueError("User daily reports require a defined 24-hour sleep/intake window")
        return self

    @field_serializer("submitted_at")
    def utc(self, value):
        return None if value is None else value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class CheckIn(CheckInInput):
    id: UUID
    provenance: Provenance


class RadiationInput(Context):
    quantity: Literal["daily_exposure_dose_msv", "cumulative_mission_dose_msv", "source_dose_rate_msv_day", "source_interval_dose_msv", "source_cumulative_dose_msv"]
    value: Annotated[float, Field(ge=0)] | None
    unit: Literal["mSv", "mSv/day"]
    dose_basis: Literal["unspecified", "effective", "dose_equivalent"]
    quality: Literal["unverified", "missing", "invalid", "conflict"]
    integration_window: Window | None
    method: Literal["source_reported", "integrated_piecewise_constant", "sum_nonoverlapping_daily_doses"]
    source_paths: Annotated[list[str], Field(min_length=1)]

    @model_validator(mode="after")
    def quantity_and_quality(self):
        if self.unit != ("mSv/day" if self.quantity == "source_dose_rate_msv_day" else "mSv"):
            raise ValueError("Dose and rate are different quantities")
        if self.quantity in ("daily_exposure_dose_msv", "cumulative_mission_dose_msv") and self.integration_window is None:
            raise ValueError("Canonical accumulated dose requires a defined integration window")
        if self.quantity == "daily_exposure_dose_msv" and (self.integration_window.end - self.integration_window.start).total_seconds() != 86400:
            raise ValueError("Daily dose requires a complete 24-hour period")
        if (self.quality == "unverified") != (self.value is not None):
            raise ValueError("Invalid, missing, or conflicting radiation must be null")
        return self


class RadiationReading(RadiationInput):
    id: UUID
    provenance: Provenance


class SensorHealth(Model):
    id: UUID
    measurement_id: UUID
    channel: Literal["heart_rate_bpm", "spo2_percent", "respiratory_rate_per_min"]
    source_reported_status: str | None
    hardware_model_claim: str | None
    quality: Literal["unverified", "missing", "invalid", "conflict"]
    issue_codes: list[Literal["VALUE_MISSING", "INVALID_VALUE", "ALIAS_CONFLICT", "STATUS_UNREPORTED", "SOURCE_STATUS_NOT_VALID"]]
    connectivity: Literal["unknown", "source_reported_disconnected"]
    last_source_sample_at: AwareDatetime
    last_non_null_sample_at: AwareDatetime | None
    synthetic: Literal[True]

    @field_serializer("last_source_sample_at", "last_non_null_sample_at")
    def utc(self, value):
        return None if value is None else value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class StatisticalObservation(Model):
    id: UUID
    astronaut_id: UUID
    mission_id: UUID
    measurement_ids: Annotated[list[UUID], Field(min_length=1)]
    detected_at: AwareDatetime
    activity_context: str
    metric: Literal["heart_rate_bpm", "spo2_percent", "respiratory_rate_per_min"]
    method: Literal["median_mad", "ewma"]
    algorithm_version: Annotated[str, Field(min_length=1)]
    baseline_id: UUID
    score: float
    explanation: Annotated[str, Field(min_length=1)]
    synthetic: Literal[True]

    @field_serializer("detected_at")
    def utc(self, value):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ResearchSource(Model):
    id: UUID
    title: str
    url: Annotated[str, Field(pattern=r"^https://")]
    agency: str
    source_version: str | None
    accessed_at: AwareDatetime
    locator: str | None
    supported_claim: str
    limitation: str
    verification_state: Literal["context_checked", "claim_unverified", "claim_conflict", "team_reviewed"]
    source_claimed_verification: str | None
    used_as_dataset: Literal[False]
    active_for_evaluation: Literal[False]

    @field_serializer("accessed_at")
    def utc(self, value):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class AcknowledgeInput(Model):
    acknowledged: Literal[True]
    note: Annotated[str, Field(max_length=500)]


MODELS = {model.__name__: model for model in (
    Astronaut, MeasurementInput, Measurement, CheckInInput, CheckIn,
    RadiationInput, RadiationReading, SensorHealth, StatisticalObservation,
    ResearchSource, AcknowledgeInput,
)}

if __name__ == "__main__":
    destination = Path(__file__).parent
    for name, model in MODELS.items():
        schema = model.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        (destination / f"{name}.schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(MODELS)} design schemas; no backend implemented.")
