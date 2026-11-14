import { mockDashboard } from "./mock-data";
import type { DashboardData } from "./contracts";
import type { CheckInInput, CheckInRecord, DemoScenario, WorkspaceData } from "./contracts";
import { astronauts, createWorkspaceFixture } from "./mission-fixtures";

// Integration seam: replace this adapter after the draft API is agreed.
// Never silently substitute mock readings for a failed future API request.
export async function getDashboardData(): Promise<DashboardData> {
  return structuredClone(mockDashboard);
}

export async function getWorkspaceData(subjectId: string, scenario: DemoScenario, signal?: AbortSignal): Promise<WorkspaceData> {
  await new Promise<void>((resolve, reject) => {
    if (signal?.aborted) { reject(new DOMException("Aborted", "AbortError")); return; }
    const abort = () => { clearTimeout(timer); reject(new DOMException("Aborted", "AbortError")); };
    const timer = setTimeout(() => { signal?.removeEventListener("abort", abort); resolve(); }, 350);
    signal?.addEventListener("abort", abort, { once: true });
  });
  if (scenario === "error") throw new Error("The mock adapter is simulating an unavailable telemetry service. Select Recorded session and retry.");
  const response = createWorkspaceFixture(subjectId);
  if (scenario === "empty") return { ...response, samples: [], observations: [], radiation: [] };
  return response;
}

const storageKey = (subjectId: string) => `cybernova-check-ins-v1:${subjectId}`;
export function validateCheckIn(input: CheckInInput): Partial<Record<keyof CheckInInput, string>> {
  const errors: Partial<Record<keyof CheckInInput, string>> = {};
  if (!Number.isFinite(input.sleepHours) || input.sleepHours < 0 || input.sleepHours > 24) errors.sleepHours = "Enter sleep duration between 0 and 24 hours.";
  if (!Number.isInteger(input.fatigueScore) || input.fatigueScore < 1 || input.fatigueScore > 10) errors.fatigueScore = "Choose a whole-number fatigue score from 1 to 10.";
  if (!Number.isFinite(input.hydrationMl) || input.hydrationMl < 0 || input.hydrationMl > 10000) errors.hydrationMl = "Enter intake between 0 and 10,000 mL. This is a form limit, not a recommendation.";
  if (input.notes.length > 500) errors.notes = "Keep notes to 500 characters or fewer.";
  return errors;
}
export function getCheckIns(subjectId: string): CheckInRecord[] {
  const parsed: unknown = JSON.parse(localStorage.getItem(storageKey(subjectId)) ?? "[]");
  if (!Array.isArray(parsed) || !parsed.every((record) => record && typeof record === "object" && record.subjectId === subjectId && typeof record.id === "string" && typeof record.submittedAt === "string" && !Number.isNaN(Date.parse(record.submittedAt)) && record.source === "mock" && typeof record.notes === "string" && Object.keys(validateCheckIn(record)).length === 0)) throw new Error("Saved demo check-ins could not be read. Browser storage may be unavailable or contain invalid data.");
  return parsed as CheckInRecord[];
}
export async function submitCheckIn(subjectId: string, input: CheckInInput): Promise<CheckInRecord> {
  if (!astronauts.some((person) => person.id === subjectId)) throw new Error("Choose a valid fictional crew member.");
  if (Object.keys(validateCheckIn(input)).length) throw new Error("Correct the highlighted check-in fields.");
  await new Promise((resolve) => setTimeout(resolve, 400));
  const record: CheckInRecord = { ...input, notes: input.notes.trim(), subjectId, id: crypto.randomUUID(), submittedAt: new Date().toISOString(), source: "mock" };
  const previous = getCheckIns(subjectId);
  localStorage.setItem(storageKey(subjectId), JSON.stringify([record, ...previous].slice(0, 30)));
  return record;
}
