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
export interface HistoricalSample extends TelemetrySample {
  activity: "Rest" | "Exercise" | "Lab work";
  quality: "Complete" | "Signal gap";
}
export interface Observation {
  id: string;
  title: string;
  category: "Statistical deviation" | "Sensor failure";
  timestamp: string;
  explanation: string;
  context: string;
  resolved: boolean;
}
export interface RadiationSample { day: string; dailyMicroSv: number; cumulativeMilliSv: number; }
export interface WorkspaceData {
  source: "mock";
  synthetic: true;
  astronaut: Astronaut;
  samples: HistoricalSample[];
  observations: Observation[];
  radiation: RadiationSample[];
}
export interface CheckInInput { sleepHours: number; fatigueScore: number; fatigueScale: "samn_perelli_1_7"; hydrationMl: number; notes: string; }
export type CheckInRecord = Omit<CheckInInput, "fatigueScale"> & { fatigueScale: "samn_perelli_1_7" | "legacy_demo_1_10"; id: string; subjectId: string; submittedAt: string; source: "mock"; };
