from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class MissionRow(Base):
    __tablename__ = "missions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    start_at: Mapped[str] = mapped_column(String(40), nullable=False)
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class AstronautRow(Base):
    __tablename__ = "astronauts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)

class AliasRow(Base):
    __tablename__ = "astronaut_aliases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), nullable=False)
    astronaut_id: Mapped[str] = mapped_column(ForeignKey("astronauts.id"), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    __table_args__ = (UniqueConstraint("mission_id", "namespace", "value"),)

class SourceSessionRow(Base):
    __tablename__ = "source_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), nullable=False)
    source_format: Mapped[str] = mapped_column(String(40), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=False)
    allowed_aliases_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

class IngestRow(Base):
    __tablename__ = "ingests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_session_id: Mapped[str] = mapped_column(ForeignKey("source_sessions.id"), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(200), nullable=False)
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_body: Mapped[str] = mapped_column(Text, nullable=False)
    receipt_json: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[str] = mapped_column(String(40), nullable=False)
    __table_args__ = (UniqueConstraint("source_session_id", "source_record_id"),)

class ResourceRow(Base):
    __tablename__ = "resources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), nullable=False)
    astronaut_id: Mapped[str] = mapped_column(ForeignKey("astronauts.id"), nullable=False)
    event_at: Mapped[str] = mapped_column(String(40), nullable=False)
    ingest_id: Mapped[str] = mapped_column(ForeignKey("ingests.id"), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)

Index("ix_resource_history", ResourceRow.kind, ResourceRow.mission_id, ResourceRow.astronaut_id, ResourceRow.event_at, ResourceRow.id)

class SensorHealthRow(Base):
    __tablename__ = "sensor_health"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    measurement_id: Mapped[str] = mapped_column(ForeignKey("resources.id"), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)

class StatisticalObservationRow(Base):
    __tablename__ = "statistical_observations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mission_id: Mapped[str] = mapped_column(ForeignKey("missions.id"), nullable=False, index=True)
    astronaut_id: Mapped[str] = mapped_column(ForeignKey("astronauts.id"), nullable=False, index=True)
    detected_at: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    metric: Mapped[str] = mapped_column(String(40), nullable=False)
    activity_context: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)

Index("ix_statistical_observations_scope", StatisticalObservationRow.mission_id, StatisticalObservationRow.astronaut_id, StatisticalObservationRow.detected_at)

class AckRow(Base):
    __tablename__ = "alert_acknowledgments"
    alert_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    acknowledged_at: Mapped[str] = mapped_column(String(40), nullable=False)
    note: Mapped[str] = mapped_column(String(500), nullable=False)
