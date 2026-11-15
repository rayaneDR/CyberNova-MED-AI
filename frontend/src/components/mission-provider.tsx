"use client";
import { createContext, useContext, useEffect, useState } from "react";
import type { DataMode, DemoScenario, WorkspaceData, Astronaut } from "@/lib/contracts";
import { getWorkspaceData } from "@/lib/data-source";
import { backendConfig, getApiAstronauts, getLiveWorkspace } from "@/lib/api-client";
import { astronauts as demoAstronauts } from "@/lib/mission-fixtures";

type LoadState = { status: "loading" } | { status: "error"; message: string } | { status: "ready"; data: WorkspaceData };
interface MissionContextValue {
  mode: DataMode; subjectId: string; astronauts: Astronaut[]; missionId: string; checkInSessionId: string;
  scenario: DemoScenario; state: LoadState;
  selectSubject: (id: string) => void; selectScenario: (value: DemoScenario) => void; selectMode: (value: DataMode) => void; retry: () => void;
}
const MissionContext = createContext<MissionContextValue | null>(null);
const modeStorageKey = "cybernova-data-mode-v1";

export function MissionProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<DataMode>("demo");
  const [preferencesReady, setPreferencesReady] = useState(false);
  const [subjectId, setSubjectId] = useState("demo-crew-01");
  const [crew, setCrew] = useState<Astronaut[]>(demoAstronauts);
  const [scenario, setScenario] = useState<DemoScenario>("nominal");
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    try { if (localStorage.getItem(modeStorageKey) === "live") setMode("live"); }
    finally { setPreferencesReady(true); }
  }, []);
  useEffect(() => { if (preferencesReady) localStorage.setItem(modeStorageKey, mode); }, [mode, preferencesReady]);

  useEffect(() => {
    if (!preferencesReady) return;
    const controller = new AbortController();
    const load = async () => {
      if (mode === "demo") {
        setCrew(demoAstronauts);
        const demoSubject = demoAstronauts.some((person) => person.id === subjectId) ? subjectId : demoAstronauts[0].id;
        if (demoSubject !== subjectId) setSubjectId(demoSubject);
        const data = await getWorkspaceData(demoSubject, scenario, controller.signal);
        if (!controller.signal.aborted) setState({ status: "ready", data });
        return;
      }
      const liveCrew = await getApiAstronauts(controller.signal);
      if (controller.signal.aborted) return;
      if (liveCrew.length === 0) throw new Error("The backend returned no astronauts for this mission. Seed a demo mission, then retry.");
      setCrew(liveCrew);
      const chosen = liveCrew.find((person) => person.id === subjectId)
        ?? liveCrew.find((person) => person.id === backendConfig.preferredAstronautId)
        ?? liveCrew[0];
      if (chosen.id !== subjectId) setSubjectId(chosen.id);
      const data = await getLiveWorkspace(chosen, controller.signal);
      if (!controller.signal.aborted) setState({ status: "ready", data });
    };
    load().catch((error: unknown) => {
      if (!controller.signal.aborted) setState({ status: "error", message: error instanceof Error ? error.message : "Unexpected backend response." });
    });
    return () => controller.abort();
  }, [mode, subjectId, scenario, revision, preferencesReady]);

  return <MissionContext.Provider value={{ mode, subjectId, astronauts: crew, missionId: backendConfig.missionId, checkInSessionId: backendConfig.checkInSessionId, scenario, state,
    selectSubject: (id) => { if (id !== subjectId) { setState({ status: "loading" }); setSubjectId(id); } },
    selectScenario: (value) => { if (value !== scenario) { setState({ status: "loading" }); setScenario(value); } },
    selectMode: (value) => { if (value !== mode) { setState({ status: "loading" }); setMode(value); } },
    retry: () => { setState({ status: "loading" }); setRevision((value) => value + 1); },
  }}>{children}</MissionContext.Provider>;
}
export function useMission() {
  const context = useContext(MissionContext);
  if (!context) throw new Error("MissionProvider is required.");
  return context;
}
