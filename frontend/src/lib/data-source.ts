import { mockDashboard } from "./mock-data";
import type { DashboardData } from "./contracts";

// Integration seam: replace this adapter after the draft API is agreed.
// Never silently substitute mock readings for a failed future API request.
export async function getDashboardData(): Promise<DashboardData> {
  return structuredClone(mockDashboard);
}
