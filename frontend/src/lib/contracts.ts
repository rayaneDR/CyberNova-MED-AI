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
