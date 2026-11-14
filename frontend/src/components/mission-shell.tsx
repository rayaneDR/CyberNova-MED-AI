"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BookOpen, CircleCheck, ClipboardList, LayoutDashboard, Orbit, Radio, Radiation, TriangleAlert } from "lucide-react";
import { astronauts, mission } from "@/lib/mission-fixtures";
import { useMission } from "./mission-provider";
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
  const { subjectId, selectSubject, scenario, selectScenario, state } = useMission();
  const title = navigation.find((item) => item.href === pathname)?.label ?? "Mission workspace";
  return <div className="app-shell"><a className="skip-link" href="#main">Skip to content</a><aside className="sidebar">
    <Link href="/" className="brand" aria-label="CyberNova MED AI overview"><span className="brand-symbol"><Orbit size={27} /></span><span>CyberNova<span className="brand-sub">MED AI</span></span></Link>
    <div className="mission-tag"><span className="status-dot" />Asteria expedition<span className="muted">Demo mission</span></div>
    <nav aria-label="Main navigation">{navigation.map(({ href, label, Icon }) => <Link key={href} href={href} aria-current={pathname === href ? "page" : undefined} className={pathname === href ? "nav-link active" : "nav-link"}><Icon size={19} aria-hidden="true" />{label}</Link>)}</nav>
    <div className="sidebar-bottom"><div className="connection"><Radio size={17} /><span>Recorded telemetry</span></div><p>Fictional crew. Synthetic readings.<br />No live sensors connected.</p><div className="team-avatar">CX<span>CyberNova X<small>Meknes 2026</small></span></div></div>
    </aside><div className="main-shell"><header className="topbar"><div className="breadcrumb">Mission control<span>/</span><strong>{title}</strong></div><div className="topbar-status"><span className="badge cyan">Synthetic demo</span><span className="muted">14 Nov 2026</span></div></header>
    <div className="workspace-heading"><div><h1>{title}</h1><p>{mission.name} <span className="separator">/</span> Crew health & performance</p></div><label className="crew-picker"><span>Astronaut · fictional</span><select value={subjectId} onChange={(event) => selectSubject(event.target.value)}>{astronauts.map((person) => <option key={person.id} value={person.id}>{person.name}</option>)}</select></label></div>
    <div className="demo-notice"><CircleCheck size={16} aria-hidden="true" /><p>All readings are synthetic. Observations are illustrative, with no diagnosis or treatment advice.</p><details className="demo-controls"><summary>Demo controls</summary><label>Adapter response<select value={scenario} onChange={(event) => selectScenario(event.target.value as DemoScenario)}><option value="nominal">Recorded session</option><option value="empty">Empty session</option><option value="error">Service error</option></select></label><small>These controls simulate data states; no live service is contacted.</small></details></div>
    <main id="main" tabIndex={-1}>{children}</main><footer><span>CyberNova X / Space Apps Meknes 2026</span><span>{state.status === "loading" ? "Loading mock response…" : "Frontend demonstration"}<span className="separator">/</span>No NASA endorsement</span></footer></div></div>;
}
