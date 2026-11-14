import { Activity, Droplets, Heart, Moon, Orbit, Waves, Wind } from "lucide-react";
import { TelemetryChart } from "@/components/telemetry-chart";
import { getDashboardData } from "@/lib/data-source";

export default async function Home() {
  const data = await getDashboardData();
  const latest = data.samples.at(-1);
  if (!latest) return <main><h1>No telemetry available</h1><p>The demo fixture is empty.</p></main>;
  const indicators = [
    { label: "Heart rate", value: latest.heartRateBpm, unit: "bpm", Icon: Heart, note: "Latest sample" },
    { label: "SpO₂", value: latest.spo2Percent, unit: "%", Icon: Waves, note: "Latest sample" },
    { label: "Respiratory rate", value: latest.respiratoryRatePerMin, unit: "/min", Icon: Wind, note: "Latest sample" },
    { label: "Sleep duration", value: latest.sleepHours, unit: "h", Icon: Moon, note: "Illustrative daily total" },
    { label: "Fatigue", value: latest.fatigueScore, unit: "/10", Icon: Activity, note: "Illustrative score · higher = more" },
    { label: "Hydration", value: latest.hydrationPercent, unit: "%", Icon: Droplets, note: "Illustrative index · not measured" },
  ];
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="masthead"><div className="brand"><Orbit size={30} aria-hidden="true" /><span>CyberNova <strong>MED AI</strong></span></div><span className="team-label">CyberNova X / Meknes 2026</span></header>
      <main id="main">
        <div className="intro"><div><p className="context">Crew telemetry demonstrator</p><h1>A window into crew wellbeing.</h1><p>Six indicators, one shared view. Explore a fixed, fictional crew session.</p></div><span className="demo-badge">Synthetic data</span></div>
        <aside className="notice"><strong>Demonstration only.</strong> Every reading is synthetic. This prototype provides no medical diagnosis, clinical risk assessment, or automatic treatment advice.</aside>
        <section aria-labelledby="crew-heading">
          <div className="crew-strip"><h2 id="crew-heading">Demo crew 01</h2><span>Recorded fixture · {latest.timestamp.slice(0, 10)} · {latest.timestamp.slice(11, 16)} UTC</span></div>
          <div className="indicators">{indicators.map(({ label, value, unit, Icon, note }) => <article className="indicator" key={label}><div className="indicator-title"><h3>{label}</h3><Icon size={20} aria-hidden="true" /></div><p className="reading">{value ?? "—"}<span>{unit}</span></p><p className="indicator-note">{note}</p></article>)}</div>
        </section>
        <div className="workspace-grid"><TelemetryChart samples={data.samples} /><aside className="mission-note"><Orbit size={36} aria-hidden="true" /><h2>Built for the human side of spaceflight.</h2><p>A collaboration between frontend, API, analytics, simulation, and research. The demo currently runs entirely on fixed fixtures.</p><h3>Scientific context</h3><p>NASA’s Human Research Program documents risks associated with spaceflight. These sources provide context; they do not validate our demo scores.</p><a href="https://www.nasa.gov/hrp/risks/" target="_blank" rel="noreferrer">Explore NASA’s human research risks (new tab)</a></aside></div>
      </main>
      <footer><span>CyberNova X · NASA Space Apps Challenge Meknes 2026 participant project</span><span>Independent prototype · No NASA endorsement</span></footer>
    </>
  );
}
