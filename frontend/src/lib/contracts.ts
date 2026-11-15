// Draft v0.1, mirrored in shared/contracts/telemetry.schema.json.
export interface TelemetrySample {
  schemaVersion: "0.1";
  subjectId: string;
  timestamp: string;
  synthetic: boolean;
  heartRateBpm: number | null;
  spo2Percent: number | null;
  respiratoryRatePerMin: number | null;
  sleepHours: number | null;
  fatigueScore: number | null; // Illustrative 0–10, higher means more fatigue.
  hydrationPercent: number | null; // Illustrative 0–100 index, not a measurement.
}

export interface DashboardData {
  source: "mock";
  synthetic: true;
  samples: TelemetrySample[];
}

// Frontend-only mock extensions. These do not change the shared v0.1 API contract.
export type Screen = "overview" | "health" | "alerts" | "check-in" | "radiation" | "research";
export type DemoScenario = "nominal" | "empty" | "error";
export interface Astronaut { id: string; name: string; initials: string; role: string; }
export type DataMode = "demo" | "live";
export interface HistoricalSample extends TelemetrySample {
  activity: "Rest" | "Exercise" | "Lab work" | "Sleep" | "EVA prep" | "EVA active" | "Unknown";
  quality: "Complete" | "Signal gap";
  channelQuality?: { heartRate: string; spo2: string; respiratoryRate: string };
  missionDay?: number | null;
  measurementId?: string;
}
export interface Observation {
  id: string;
  title: string;
  category: "Statistical deviation" | "Sensor failure" | "Sensor data issue";
  timestamp: string;
  explanation: string;
  context: string;
  resolved: boolean;
  source?: "mock" | "api";
  acknowledgment?: { actorId: string; acknowledgedAt: string; note: string } | null;
  metric?: string;
  method?: "median_mad" | "ewma";
  observationType?: "robust_deviation" | "sustained_ewma_shift" | "combined_deviation";
  status?: "STATISTICAL_DEVIATION" | "SENSOR_DATA_ISSUE";
  quality?: string;
  sourceFormat?: string;
  activityContext?: string;
  supportingValues?: Record<string, number>;
}
export interface RadiationSample { day: string; dailyMicroSv: number | null; cumulativeMilliSv: number | null; dailyDoseMsv?: number | null; sourceDoseRateMsvDay?: number | null; }
export interface SensorQuality { channel: string; quality: string; connectivity: string; issueCodes: string[]; sourceStatus?: string | null; lastSampleAt?: string; }
export interface RadiationReadingView {
  id: string; observedAt: string; quantity: "daily_exposure_dose_msv" | "cumulative_mission_dose_msv" | "source_dose_rate_msv_day" | "source_interval_dose_msv" | "source_cumulative_dose_msv";
  value: number | null; unit: "mSv" | "mSv/day"; quality: string; windowStart: string | null; windowEnd: string | null;
}
export interface WorkspaceData {
  source: "mock" | "api";
  synthetic: true;
  astronaut: Astronaut;
  missionId?: string;
  samples: HistoricalSample[];
  observations: Observation[];
  radiation: RadiationSample[];
  radiationReadings?: RadiationReadingView[];
  sourceRates?: RadiationReadingView[];
  sensorHealth?: SensorQuality[];
  checkIns?: CheckInRecord[];
  analyticsStatus?: "ready";
  baselineStatus?: "ready" | "insufficient_baseline";
  analyticsMetrics?: MetricBaselineSummary[];
  analyticsConfiguration?: AnalyticsConfiguration;
}
export interface MetricBaselineSummary {
  astronaut_id: string; metric: string; activity_context: string; status: "READY" | "INSUFFICIENT_BASELINE";
  valid_measurement_count: number; baseline_sample_count: number; baseline_median: number | null; mad: number | null;
}
export interface AnalyticsConfiguration {
  history_window: number; minimum_baseline: number; robust_z_threshold: number; baseline_guard_z: number;
  ewma_alpha: number; ewma_z_threshold: number; required_consecutive: number;
  dispersion_floors: Record<string, number>;
}
export interface CheckInInput { sleepHours: number; fatigueScore: number; fatigueScale: "samn_perelli_1_7"; hydrationMl: number; notes: string; }
export type CheckInRecord = Omit<CheckInInput, "fatigueScale"> & { fatigueScale: "samn_perelli_1_7" | "legacy_demo_1_10"; id: string; subjectId: string; submittedAt: string; source: "mock" | "api"; };
