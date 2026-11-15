import type { Astronaut, Observation, WorkspaceData } from "./contracts";

export const astronauts: Astronaut[] = [
  { id: "demo-crew-01", name: "Maya Chen", initials: "MC", role: "Mission commander" },
  { id: "demo-crew-02", name: "Adam Idrissi", initials: "AI", role: "Flight engineer" },
  { id: "demo-crew-03", name: "Leila Santos", initials: "LS", role: "Research specialist" },
];
export const mission = { name: "Asteria / Expedition 01", day: 14, duration: 30, location: "Orbital research habitat", recordedAt: "2026-11-14T12:00:00.000Z" };

// Deterministic presentation fixtures, not simulator or analytics implementations.
export function createWorkspaceFixture(subjectId: string): WorkspaceData {
  const crewIndex = astronauts.findIndex((person) => person.id === subjectId);
  if (crewIndex < 0) throw new Error("Unknown fictional crew member.");
  const astronaut = astronauts[crewIndex];
  const samples = Array.from({ length: 72 }, (_, index) => {
    const timestamp = new Date(Date.parse(mission.recordedAt) - (71 - index) * 3_600_000).toISOString();
    const exercise = index % 24 >= 15 && index % 24 <= 16;
    const gap = (crewIndex === 1 && index === 71) || index === 40;
    return {
      schemaVersion: "0.1" as const, subjectId, timestamp, synthetic: true,
      heartRateBpm: Math.round(69 + crewIndex * 3 + Math.sin(index * 0.65) * 5 + (exercise ? 24 : 0)),
      spo2Percent: gap ? null : 98 - (index % 7 === 0 ? 1 : 0),
      respiratoryRatePerMin: 15 + crewIndex + (exercise ? 5 : index % 3),
      sleepHours: 7.2 - crewIndex * 0.4, fatigueScore: 3 + crewIndex,
      hydrationPercent: 76 - crewIndex * 3,
      activity: exercise ? "Exercise" as const : index % 24 < 7 ? "Rest" as const : "Lab work" as const,
      quality: gap ? "Signal gap" as const : "Complete" as const,
    };
  });
  let cumulative = 0;
  const radiation = Array.from({ length: 14 }, (_, index) => {
    const dailyMicroSv = 270 + ((index * 37 + crewIndex * 19) % 110);
    cumulative += dailyMicroSv / 1000;
    return { day: `Nov ${String(index + 1).padStart(2, "0")}`, dailyMicroSv, cumulativeMilliSv: Number(cumulative.toFixed(3)) };
  });
  return {
    source: "mock", synthetic: true, astronaut, samples, radiation,
    observations: ([
      { id: `${subjectId}-signal`, title: "Optical sensor signal interrupted", category: "Sensor failure", timestamp: samples[crewIndex === 1 ? 71 : 40].timestamp, resolved: crewIndex !== 1,
        explanation: "A staged optical-sensor dropout produces a missing SpO₂ reading. Missing sensor data cannot establish a physiological change.", context: "Fixture event · SpO₂ unavailable during the gap; no replacement value is inferred." },
      { id: `${subjectId}-deviation`, title: "Heart rate differs from resting baseline", category: "Statistical deviation", timestamp: samples[64].timestamp, resolved: false,
        explanation: "Staged statistical observation: the fixture pairs an exercise heart rate with an illustrative resting reference of 69–75 bpm. This event is authored demo content, not the result of an implemented detection algorithm or a clinical threshold.", context: "Exercise context · requires human interpretation. Ali owns future statistical analysis." },
      { id: `${subjectId}-history`, title: "Earlier signal interruption resolved", category: "Sensor failure", timestamp: samples[16].timestamp, resolved: true,
        explanation: "Historical demonstration of a sensor reconnection. Valid samples resume after this fictional event.", context: "Recorded history · no physiological interpretation." },
    ] satisfies Observation[]).sort((a, b) => b.timestamp.localeCompare(a.timestamp)),
  };
}

export const researchSources = [
  { title: "Risks of human spaceflight", topic: "Mission context", url: "https://www.nasa.gov/hrp/risks/", support: "NASA’s Human Research Program organizes research around risks to human health and performance during spaceflight. This motivates a shared view of crew observations.", limitation: "Background reference; it does not validate our indicators, fixture values, or anomaly observations." },
  { title: "Inadequate sleep & irregular schedules", topic: "Daily check-in", url: "https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/", support: "NASA describes sleep and scheduling as a human-spaceflight research concern. This informs our decision to collect sleep duration and subjective fatigue context.", limitation: "It does not establish our fatigue scale as a validated assessment or prove a relationship in the fictional crew data." },
  { title: "Space radiation", topic: "Exposure visualization", url: "https://www.nasa.gov/hrp/hazard-space-radiation/", support: "NASA describes space radiation as a research hazard and discusses monitoring and protection research. This motivates an exposure trend view.", limitation: "No NASA dose measurements, hazard limits, or dose model are used. All displayed exposure values are invented." },
];
