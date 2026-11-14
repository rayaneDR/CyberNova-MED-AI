"use client";
import { createContext, useContext, useEffect, useState } from "react";
import type { DemoScenario, WorkspaceData } from "@/lib/contracts";
import { getWorkspaceData } from "@/lib/data-source";
type LoadState = { status: "loading" } | { status: "error"; message: string } | { status: "ready"; data: WorkspaceData };
interface MissionContextValue {
  subjectId: string; scenario: DemoScenario; state: LoadState;
  selectSubject: (id: string) => void; selectScenario: (value: DemoScenario) => void; retry: () => void;
}
const MissionContext = createContext<MissionContextValue | null>(null);
export function MissionProvider({ children }: { children: React.ReactNode }) {
  const [subjectId, setSubjectId] = useState("demo-crew-01");
  const [scenario, setScenario] = useState<DemoScenario>("nominal");
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState<LoadState>({ status: "loading" });
  useEffect(() => {
    const controller = new AbortController();
    getWorkspaceData(subjectId, scenario, controller.signal).then((data) => {
      if (!controller.signal.aborted) setState({ status: "ready", data });
    }).catch((error: Error) => {
      if (!controller.signal.aborted) setState({ status: "error", message: error.message });
    });
    return () => controller.abort();
  }, [subjectId, scenario, revision]);
  return <MissionContext.Provider value={{ subjectId, scenario, state,
    selectSubject: (id) => { if (id !== subjectId) { setState({ status: "loading" }); setSubjectId(id); } },
    selectScenario: (value) => { if (value !== scenario) { setState({ status: "loading" }); setScenario(value); } },
    retry: () => { setState({ status: "loading" }); setRevision((value) => value + 1); },
  }}>{children}</MissionContext.Provider>;
}
export function useMission() {
  const context = useContext(MissionContext);
  if (!context) throw new Error("MissionProvider is required.");
  return context;
}
