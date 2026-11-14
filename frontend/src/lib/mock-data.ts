import type { DashboardData, TelemetrySample } from "./contracts";

// Fixed fixtures are reproducible and independent of all teammates' modules.
const heartRates = [68, 70, 69, 74, 76, 72, 71, 73, 70, 69, 72, 72];
export const mockDashboard: DashboardData = {
  source: "mock",
  synthetic: true,
  samples: heartRates.map((heartRateBpm, index): TelemetrySample => ({
    schemaVersion: "0.1",
    subjectId: "demo-crew-01",
    timestamp: new Date(Date.UTC(2026, 10, 14, 8, index * 5)).toISOString(),
    synthetic: true,
    heartRateBpm,
    spo2Percent: 98,
    respiratoryRatePerMin: 16,
    sleepHours: 7.2,
    fatigueScore: 3,
    hydrationPercent: 76,
  })),
};
