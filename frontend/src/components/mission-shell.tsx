"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BookOpen, CircleCheck, ClipboardList, LayoutDashboard, Orbit, Radio, Radiation, TriangleAlert } from "lucide-react";
import { mission } from "@/lib/mission-fixtures";
import { useMission } from "./mission-provider";
import { OrbitalIntro } from "./orbital-intro";
import type { DemoScenario } from "@/lib/contracts";
const navigation = [
  { href: "/", label: "Overview", Icon: LayoutDashboard },
  { href: "/health", label: "Health monitoring", Icon: Activity },
  { href: "/alerts", label: "Alert center", Icon: TriangleAlert },
  { href: "/check-in", label: "Daily check-in", Icon: ClipboardList },
  { href: "/radiation", label: "Radiation monitoring", Icon: Radiation },
  { href: "/research", label: "NASA research", Icon: BookOpen },
];
export function MissionShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { subjectId, selectSubject, astronauts, scenario, selectScenario, mode, selectMode, state } = useMission();
  const title = navigation.find((item) => item.href === pathname)?.label ?? "Mission workspace";
  return <div className="app-shell"><a className="skip-link" href="#main">Skip to content</a><aside className="sidebar">
    <Link href="/" className="brand" aria-label="CyberNova MED AI overview"><span className="brand-symbol"><Orbit size={27} /></span><span>CyberNova<span className="brand-sub">MED AI</span></span></Link>
    <div className="mission-tag"><span className={`status-dot ${mode === "live" && state.status === "error" ? "warning" : ""}`} />Mission workspace<span className="muted">{mode === "live" ? "Backend API" : "Demo mission"}</span></div>
    <nav aria-label="Main navigation">{navigation.map(({ href, label, Icon }) => <Link key={href} href={href} aria-current={pathname === href ? "page" : undefined} className={pathname === href ? "nav-link active" : "nav-link"}><Icon size={19} aria-hidden="true" />{label}</Link>)}</nav>
    <details className="mobile-nav-picker"><summary>Navigate <span aria-hidden="true">·</span> {title}</summary><nav aria-label="Mobile navigation">{navigation.map(({ href, label, Icon }) => <Link key={href} href={href} aria-current={pathname === href ? "page" : undefined} className={pathname === href ? "nav-link active" : "nav-link"}><Icon size={18} aria-hidden="true" />{label}</Link>)}</nav></details>
    <div className="sidebar-bottom"><div className="connection"><Radio size={17} /><span>{mode === "live" ? "FastAPI · synthetic stream" : "Recorded telemetry"}</span></div><p>{mode === "live" ? "Live API records. Sensor connectivity remains source-reported or unknown." : <>Fictional crew. Synthetic readings.<br />No live sensors connected.</>}</p><div className="team-avatar">CX<span>CyberNova X<small>Meknes 2026</small></span></div></div>
    </aside><div className="main-shell"><header className="topbar"><div className="breadcrumb">Mission control<span>/</span><strong>{title}</strong></div><div className="topbar-status"><span className="badge cyan">{mode === "live" ? "Synthetic API" : "Synthetic demo"}</span><span className="muted">14 Nov 2026</span></div></header>
    <div className="workspace-heading"><div><h1>{title}</h1><p>{mode === "live" ? "Configured mission · live backend records" : `${mission.name} · demo mission`} <span className="separator">/</span> Crew health & performance</p></div><div className="toolbar-controls"><label className="mode-picker"><span>Data mode</span><select aria-label="Data mode" value={mode} onChange={(event) => selectMode(event.target.value as "demo" | "live")}><option value="demo">Demo fixtures</option><option value="live">Live API</option></select></label><label className="crew-picker"><span>Astronaut · {mode === "live" ? "API roster" : "fictional"}</span><select value={astronauts.some((person) => person.id === subjectId) ? subjectId : ""} onChange={(event) => selectSubject(event.target.value)} disabled={state.status !== "ready"}>{astronauts.map((person) => <option key={person.id} value={person.id}>{person.name}</option>)}</select></label></div></div>
    <div className="demo-notice"><CircleCheck size={16} aria-hidden="true" /><p>{mode === "live" ? "Live API mode · synthetic records only. No real sensors, diagnoses, or treatment advice." : "Demo mode · fixed synthetic fixtures. No live backend request is made."}</p>{mode === "demo" && <details className="demo-controls"><summary>Demo controls</summary><label>Adapter response<select value={scenario} onChange={(event) => selectScenario(event.target.value as DemoScenario)}><option value="nominal">Recorded session</option><option value="empty">Empty session</option><option value="error">Service error</option></select></label><small>These controls simulate the Demo adapter state.</small></details>}</div>
    <main id="main" tabIndex={-1}>{pathname === "/" && <OrbitalIntro />}{children}</main><footer><span>CyberNova X / Space Apps Meknes 2026</span><span>{state.status === "loading" ? `Loading ${mode === "live" ? "API" : "Demo"} data…` : mode === "live" ? "FastAPI / SQLite" : "Frontend demo fixtures"}<span className="separator">/</span>No NASA endorsement</span></footer></div></div>;
}
