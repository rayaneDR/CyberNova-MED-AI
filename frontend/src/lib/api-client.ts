import type { Astronaut, CheckInInput, CheckInRecord, HistoricalSample, Observation, RadiationReadingView, WorkspaceData } from "./contracts";

export type ApiReading = { value: number | null; unit: string; quality: "unverified" | "missing" | "invalid" | "conflict"; source_paths: string[] };
export type ApiProvenance = { source_format: string; source_session_id: string; source_record_id: string; source_sent_at: string | null; received_at: string; ingest_id: string; payload_sha256: string };
export type ApiMeasurement = {
  id: string; astronaut_id: string; mission_id: string; mission_day: number | null; observed_at: string; synthetic: true; activity_context: string;
  heart_rate_bpm: ApiReading; spo2_percent: ApiReading; respiratory_rate_per_min: ApiReading; provenance: ApiProvenance;
};
export type ApiSensorHealth = {
  id: string; measurement_id: string; channel: string; source_reported_status: string | null; hardware_model_claim: string | null;
  quality: ApiReading["quality"]; issue_codes: string[]; connectivity: "unknown" | "source_reported_disconnected";
  last_source_sample_at: string; last_non_null_sample_at: string | null; synthetic: true;
};
export type ApiAstronaut = { id: string; mission_id: string; display_name: string; role: string; aliases: { namespace: string; value: string }[]; synthetic: true };
export type ApiCheckIn = {
  id: string; astronaut_id: string; mission_id: string; observed_at: string; synthetic: true; report_kind: "user_demo" | "source_snapshot" | "simulator_snapshot";
  submitted_at: string | null; reporting_window: { start: string; end: string } | null; sleep_hours: number | null;
  fatigue: { value: number; scale: "samn_perelli_1_7"; source_scale_label: string; assessed_at: string | null } | null;
  legacy_fatigue: { value: number; scale: "source_ordinal_1_10"; source_scale_label: string; source_path: string } | null;
  hydration_intake_ml: number | null; notes: string; provenance: ApiProvenance;
};
export type ApiRadiation = {
  id: string; astronaut_id: string; mission_id: string; observed_at: string; synthetic: true;
  quantity: RadiationReadingView["quantity"]; value: number | null; unit: "mSv" | "mSv/day"; quality: string;
  dose_basis: string; integration_window: { start: string; end: string } | null; method: string; source_paths: string[]; provenance: ApiProvenance;
};
export type ApiAlert = {
  id: string; astronaut_id: string; mission_id: string; detected_at: string; kind: "sensor_data_issue" | "statistical_observation"; synthetic: true;
  sensor_health: ApiSensorHealth | null; statistical_observation: { metric: string; method: string; explanation: string; score: number; algorithm_version: string } | null;
  acknowledgment: { actor_id: string; acknowledged_at: string; note: string } | null;
};
export type ApiList<T> = { items: T[]; next_cursor: string | null; synthetic: true };
type MeasurementList = ApiList<ApiMeasurement> & { sensor_health: ApiSensorHealth[] };
type AnalyticsSummary = { astronaut_id: string; mission_id: string; analytics_status: "not_configured"; baseline_status: "unavailable"; statistical_observations_count: null; latest_measurement_at: string | null; summary: null; synthetic: true };
type CheckInPost = { item: ApiCheckIn; duplicate: boolean };

export const backendConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "",
  missionId: process.env.NEXT_PUBLIC_MISSION_ID ?? "",
  checkInSessionId: process.env.NEXT_PUBLIC_SOURCE_SESSION_ID ?? "",
  preferredAstronautId: process.env.NEXT_PUBLIC_ASTRONAUT_ID ?? "",
};

function requireConfig(): void {
  if (!backendConfig.baseUrl) throw new Error("Live mode is not configured. Set NEXT_PUBLIC_API_BASE_URL and restart Next.js.");
  if (!backendConfig.missionId) throw new Error("Live mode needs NEXT_PUBLIC_MISSION_ID from the backend seed-demo output.");
}

async function request<T>(path: string, signal?: AbortSignal, init?: RequestInit): Promise<T> {
  requireConfig();
  let response: Response;
  try {
    response = await fetch(`${backendConfig.baseUrl}${path}`, { ...init, signal, cache: "no-store", headers: { ...(init?.body ? { "Content-Type": "application/json" } : {}), ...init?.headers } });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new Error(`Backend is unreachable at ${backendConfig.baseUrl}. Check FastAPI and CORS, then retry.`);
  }
  if (!response.ok) {
    let message = `Backend request failed (${response.status}).`;
    try { const body = await response.json() as { detail?: { error?: { message?: string } } | string }; const detail = body.detail; message = typeof detail === "string" ? detail : detail?.error?.message ?? message; } catch { /* keep status fallback */ }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

function listPath(path: string, missionId: string, astronautId: string, limit = 500, cursor?: string | null): string {
  const [pathname, existingQuery] = path.split("?");
  const query = new URLSearchParams(existingQuery ?? "");
  query.set("mission_id", missionId); query.set("astronaut_id", astronautId); query.set("limit", String(limit));
  if (cursor) query.set("cursor", cursor);
  return `${pathname}?${query}`;
}
async function allPages<T>(path: string, missionId: string, astronautId: string, signal?: AbortSignal): Promise<T[]> {
  const items: T[] = []; let cursor: string | null = null; let pages = 0;
  do {
    const page: ApiList<T> & Record<string, unknown> = await request<ApiList<T> & Record<string, unknown>>(listPath(path, missionId, astronautId, 500, cursor), signal);
    if (!Array.isArray(page.items) || page.synthetic !== true) throw new Error(`Invalid ${path} response from the backend.`);
    items.push(...page.items); cursor = page.next_cursor; pages += 1;
    if (pages > 100) throw new Error(`The ${path} response exceeded the 50,000-record display limit.`);
  } while (cursor);
  return items;
}
async function allMeasurementPages(missionId: string, astronautId: string, signal?: AbortSignal): Promise<{ items: ApiMeasurement[]; health: ApiSensorHealth[] }> {
  const items: ApiMeasurement[] = []; const health: ApiSensorHealth[] = []; let cursor: string | null = null; let pages = 0;
  do {
    const page: MeasurementList = await request<MeasurementList>(listPath("/measurements", missionId, astronautId, 500, cursor), signal);
    if (!Array.isArray(page.items) || !Array.isArray(page.sensor_health) || page.synthetic !== true) throw new Error("Invalid /measurements response from the backend.");
    items.push(...page.items); health.push(...page.sensor_health); cursor = page.next_cursor; pages += 1;
    if (pages > 100) throw new Error("The /measurements response exceeded the 50,000-record display limit.");
  } while (cursor);
  return { items, health };
}

export async function getApiAstronauts(signal?: AbortSignal): Promise<Astronaut[]> {
  requireConfig();
  const result = await request<ApiList<ApiAstronaut>>(`/astronauts?mission_id=${encodeURIComponent(backendConfig.missionId)}`, signal);
  if (!Array.isArray(result.items) || result.synthetic !== true) throw new Error("Invalid astronaut roster response from the backend.");
  return result.items.map((person) => ({ id: person.id, name: person.display_name, initials: person.display_name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase(), role: person.role }));
}

function activityLabel(value: string): HistoricalSample["activity"] {
  return ({ RESTING: "Rest", SLEEP: "Sleep", EXERCISE: "Exercise", EVA_PREP: "EVA prep", EVA_ACTIVE: "EVA active", LAB_WORK: "Lab work" } as Record<string, HistoricalSample["activity"]>)[value] ?? "Unknown";
}
function sampleFromApi(measurement: ApiMeasurement): HistoricalSample {
  const hr = measurement.heart_rate_bpm, spo2 = measurement.spo2_percent, rr = measurement.respiratory_rate_per_min;
  const qualities = [hr.quality, spo2.quality, rr.quality];
  return {
    schemaVersion: "0.1", subjectId: measurement.astronaut_id, timestamp: measurement.observed_at, synthetic: true,
    heartRateBpm: hr.value, spo2Percent: spo2.value, respiratoryRatePerMin: rr.value, sleepHours: null, fatigueScore: null, hydrationPercent: null,
    activity: activityLabel(measurement.activity_context), quality: qualities.every((quality) => quality === "unverified") ? "Complete" : "Signal gap",
    channelQuality: { heartRate: hr.quality, spo2: spo2.quality, respiratoryRate: rr.quality }, missionDay: measurement.mission_day, measurementId: measurement.id,
  };
}
function radiationView(record: ApiRadiation): RadiationReadingView {
  return { id: record.id, observedAt: record.observed_at, quantity: record.quantity, value: record.value, unit: record.unit, quality: record.quality, windowStart: record.integration_window?.start ?? null, windowEnd: record.integration_window?.end ?? null };
}
function checkInView(record: ApiCheckIn): CheckInRecord | null {
  if (record.report_kind !== "user_demo" || !record.fatigue || record.sleep_hours === null || record.hydration_intake_ml === null || !record.submitted_at) return null;
  return { id: record.id, subjectId: record.astronaut_id, submittedAt: record.submitted_at, sleepHours: record.sleep_hours, fatigueScore: record.fatigue.value,
    fatigueScale: "samn_perelli_1_7", hydrationMl: record.hydration_intake_ml, notes: record.notes, source: "api" };
}
function observationFromApi(alert: ApiAlert): Observation {
  const health = alert.sensor_health, statistical = alert.statistical_observation;
  const channelName = health?.channel.replaceAll("_", " ") ?? statistical?.metric ?? "Observation";
  return { id: alert.id, title: health ? `${channelName} · ${health.issue_codes.join(", ") || health.quality}` : `${statistical?.metric ?? "Statistical"} observation`,
    category: alert.kind === "sensor_data_issue" ? "Sensor failure" : "Statistical deviation", timestamp: alert.detected_at,
    explanation: health ? `Source reported ${health.quality} data. This is a data-quality observation, not a physiological conclusion.` : statistical?.explanation ?? "Statistical observation supplied by the analytics service.",
    context: health ? `Connectivity: ${health.connectivity}. Source status: ${health.source_reported_status ?? "not reported"}.` : `Method ${statistical?.method ?? "not supplied"}; version ${statistical?.algorithm_version ?? "not supplied"}.`, resolved: alert.acknowledgment !== null, source: "api",
    acknowledgment: alert.acknowledgment ? { actorId: alert.acknowledgment.actor_id, acknowledgedAt: alert.acknowledgment.acknowledged_at, note: alert.acknowledgment.note } : null };
}

export async function getLiveWorkspace(astronaut: Astronaut, signal?: AbortSignal): Promise<WorkspaceData> {
  requireConfig();
  const missionId = backendConfig.missionId;
  const [measurementResult, alerts, radiation, sourceRates, checkins, analytics] = await Promise.all([
    allMeasurementPages(missionId, astronaut.id, signal),
    allPages<ApiAlert>("/alerts", missionId, astronaut.id, signal),
    allPages<ApiRadiation>("/radiation", missionId, astronaut.id, signal),
    allPages<ApiRadiation>("/radiation?quantity=source_dose_rate_msv_day", missionId, astronaut.id, signal),
    allPages<ApiCheckIn>("/checkins", missionId, astronaut.id, signal),
    request<AnalyticsSummary>(`/analytics/summary?mission_id=${encodeURIComponent(missionId)}&astronaut_id=${encodeURIComponent(astronaut.id)}`, signal),
  ]);
  const measurements = measurementResult.items;
  const samples = measurements.map(sampleFromApi).sort((a, b) => a.timestamp.localeCompare(b.timestamp));
  const daily = radiation.filter((item) => item.quantity === "daily_exposure_dose_msv" || item.quantity === "cumulative_mission_dose_msv");
  const radiationReadings = daily.map(radiationView);
  const sourceRateViews = sourceRates.map(radiationView);
  const dates = [...daily].sort((a, b) => a.observed_at.localeCompare(b.observed_at));
  const allDoseAndRateDates = [...dates, ...sourceRateViews.map((item) => ({ observed_at: item.observedAt, quantity: item.quantity, value: item.value }))].sort((a, b) => a.observed_at.localeCompare(b.observed_at));
  const radiationChart = [...new Set(allDoseAndRateDates.map((item) => item.observed_at.slice(0, 10)))].map((day) => ({ day, dailyMicroSv: null as number | null, cumulativeMilliSv: null as number | null, dailyDoseMsv: null as number | null, sourceDoseRateMsvDay: null as number | null }));
  for (const item of dates) {
    const index = radiationChart.findIndex((point) => point.day === item.observed_at.slice(0, 10));
    if (index >= 0 && item.quantity === "daily_exposure_dose_msv") radiationChart[index].dailyDoseMsv = item.value;
    if (index >= 0 && item.quantity === "cumulative_mission_dose_msv") radiationChart[index].cumulativeMilliSv = item.value;
  }
  for (const item of sourceRateViews) { const point = radiationChart.find((row) => row.day === item.observedAt.slice(0, 10)); if (point) point.sourceDoseRateMsvDay = item.value; }
  return { source: "api", synthetic: true, missionId, astronaut, samples, observations: alerts.map(observationFromApi).sort((a, b) => b.timestamp.localeCompare(a.timestamp)),
    radiation: radiationChart, radiationReadings, sourceRates: sourceRateViews,
    sensorHealth: measurementResult.health.map((sensor) => ({ channel: sensor.channel, quality: sensor.quality, connectivity: sensor.connectivity, issueCodes: sensor.issue_codes, sourceStatus: sensor.source_reported_status, lastSampleAt: sensor.last_source_sample_at })),
    checkIns: checkins.map(checkInView).filter((item): item is CheckInRecord => item !== null), analyticsStatus: analytics.analytics_status };
}

export async function getLiveCheckIns(missionId: string, astronautId: string, signal?: AbortSignal): Promise<CheckInRecord[]> {
  const records = await allPages<ApiCheckIn>("/checkins", missionId, astronautId, signal);
  return records.map(checkInView).filter((item): item is CheckInRecord => item !== null);
}
export async function submitLiveCheckIn(missionId: string, astronautId: string, input: CheckInInput): Promise<CheckInRecord> {
  if (!backendConfig.checkInSessionId) throw new Error("Live check-in is not configured. Set NEXT_PUBLIC_SOURCE_SESSION_ID from seed-demo and restart Next.js.");
  const submitted = new Date(); const end = submitted.toISOString(); const start = new Date(submitted.getTime() - 86_400_000).toISOString();
  const requestBody = { astronaut_id: astronautId, mission_id: missionId, mission_day: null, observed_at: end, synthetic: true, report_kind: "user_demo", submitted_at: end,
    reporting_window: { start, end }, sleep_hours: input.sleepHours, fatigue: { value: input.fatigueScore, scale: input.fatigueScale, source_scale_label: "Samn–Perelli proposed MVP scale", assessed_at: end },
    legacy_fatigue: null, hydration_intake_ml: input.hydrationMl, notes: input.notes.trim() };
  const result = await request<CheckInPost>(`/checkins?source_session_id=${encodeURIComponent(backendConfig.checkInSessionId)}`, undefined,
    { method: "POST", headers: { "Idempotency-Key": crypto.randomUUID() }, body: JSON.stringify(requestBody) });
  const mapped = checkInView(result.item);
  if (!mapped) throw new Error("Backend accepted a check-in that did not match the user-report contract.");
  return mapped;
}

export async function acknowledgeLiveAlert(alertId: string, note: string): Promise<void> {
  await request<{ item: ApiAlert }>(`/alerts/${encodeURIComponent(alertId)}/acknowledge`, undefined,
    { method: "PATCH", body: JSON.stringify({ acknowledged: true, note }) });
}
