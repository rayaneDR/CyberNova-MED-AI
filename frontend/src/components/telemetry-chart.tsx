"use client";
import { useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { HistoricalSample, RadiationSample } from "@/lib/contracts";
export const metrics = {
  heartRateBpm: { label: "Heart rate", unit: "bpm", color: "#5ce0e6" },
  spo2Percent: { label: "SpO₂", unit: "%", color: "#a4afff" },
  respiratoryRatePerMin: { label: "Respiratory rate", unit: "/min", color: "#e9ba73" },
} as const;
type Metric = keyof typeof metrics;
const tooltipStyle = { background: "#132438", border: "1px solid #40546c", borderRadius: 8, color: "#edf4ff", fontSize: 13 };
export function TelemetryChart({ samples, compact = false }: { samples: HistoricalSample[]; compact?: boolean }) {
  const [metric, setMetric] = useState<Metric>("heartRateBpm");
  const [range, setRange] = useState(24);
  const selected = metrics[metric];
  const visible = samples.slice(-range);
  const points = visible.map((sample) => ({ ...sample, time: `${sample.timestamp.slice(8, 10)} Nov ${sample.timestamp.slice(11, 16)}` }));
  return <section className="panel chart-panel" aria-labelledby="telemetry-heading"><div className="panel-heading"><div><h2 id="telemetry-heading">{compact ? "Health trends" : "Historical telemetry"}</h2><p>Hourly samples · UTC · Synthetic fixture</p></div><div className="range-buttons" aria-label="Time range">{[6, 24, 72].map((hours) => <button key={hours} aria-pressed={range === hours} onClick={() => setRange(hours)}>{hours === 72 ? "3 days" : `${hours}h`}</button>)}</div></div>
    <div className="chart-toolbar"><label>Signal<select value={metric} onChange={(event) => setMetric(event.target.value as Metric)}>{Object.entries(metrics).map(([key, value]) => <option key={key} value={key}>{value.label}</option>)}</select></label><span className="chart-key"><i style={{ background: selected.color }} />{selected.label} ({selected.unit})<span className="muted">{visible.length} samples</span></span></div>
    <div className="chart" role="img" aria-label={`Synthetic ${selected.label}, last ${visible.length} hours. Gaps mean unavailable readings. Exact values in table below.`}><ResponsiveContainer width="100%" height="100%" minWidth={0}><LineChart data={points} margin={{ top: 18, right: 20, bottom: 10, left: -10 }}><CartesianGrid stroke="#26364b" vertical={false} strokeDasharray="3 5" /><XAxis dataKey="time" tick={{ fill: "#a1b2c8", fontSize: 11 }} minTickGap={55} axisLine={false} tickLine={false} dy={10} /><YAxis tick={{ fill: "#a1b2c8", fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, "auto"]} width={52} /><Tooltip contentStyle={tooltipStyle} labelStyle={{ color: "#c3d1e4" }} formatter={(value) => [`${value} ${selected.unit}`, selected.label]} /><Line type="linear" dataKey={metric} stroke={selected.color} strokeWidth={2.5} dot={false} activeDot={{ r: 5 }} isAnimationActive={false} connectNulls={false} /></LineChart></ResponsiveContainer></div>
    <div className="chart-caption"><span>{visible[0]?.timestamp.slice(0, 16).replace("T", " ")} to {visible.at(-1)?.timestamp.slice(0, 16).replace("T", " ")} UTC</span><span>Gaps are preserved</span></div>
    <details className="data-details"><summary>View exact values and activity context</summary><div className="table-scroll"><table><caption>Synthetic {selected.label} · {visible.length} hourly samples</caption><thead><tr><th scope="col">Time (UTC)</th><th scope="col">{selected.label} ({selected.unit})</th><th scope="col">Activity</th><th scope="col">Quality</th></tr></thead><tbody>{points.map((point) => <tr key={point.timestamp}><th scope="row">{point.time}</th><td>{point[metric] ?? "Unavailable"}</td><td>{point.activity}</td><td>{point.quality}</td></tr>)}</tbody></table></div></details></section>;
}
export function RadiationChart({ samples }: { samples: RadiationSample[] }) {
  const [mode, setMode] = useState<"dailyMicroSv" | "cumulativeMilliSv">("dailyMicroSv");
  const [range, setRange] = useState(14);
  const unit = mode === "dailyMicroSv" ? "µSv/day" : "mSv";
  const visible = samples.slice(-range);
  return <section className="panel chart-panel"><div className="panel-heading"><div><h2>Exposure trend</h2><p>Invented values · no hazard thresholds</p></div><div className="range-buttons" aria-label="Radiation range">{[7, 14].map((days) => <button key={days} aria-pressed={range === days} onClick={() => setRange(days)}>{days} days</button>)}</div></div><label className="chart-toolbar">Exposure series<select value={mode} onChange={(event) => setMode(event.target.value as typeof mode)}><option value="dailyMicroSv">Daily dose rate (µSv/day)</option><option value="cumulativeMilliSv">Cumulative exposure (mSv)</option></select></label><div className="chart" role="img" aria-label={`Synthetic exposure in ${unit}. Exact values in table below.`}><ResponsiveContainer width="100%" height="100%" minWidth={0}><LineChart data={visible} margin={{ right: 20, left: -10, top: 16, bottom: 10 }}><CartesianGrid stroke="#26364b" vertical={false} strokeDasharray="3 5" /><XAxis dataKey="day" tick={{ fill: "#a1b2c8", fontSize: 12 }} axisLine={false} tickLine={false} minTickGap={25} /><YAxis tick={{ fill: "#a1b2c8", fontSize: 12 }} axisLine={false} tickLine={false} width={55} /><Tooltip contentStyle={tooltipStyle} formatter={(value) => [`${value} ${unit}`, "Synthetic exposure"]} /><Line dataKey={mode} stroke="#a4afff" strokeWidth={2.5} dot={false} isAnimationActive={false} /></LineChart></ResponsiveContainer></div><details className="data-details"><summary>View exposure values</summary><div className="table-scroll"><table><caption>Synthetic radiation values</caption><thead><tr><th scope="col">Day (2026)</th><th scope="col">Daily (µSv/day)</th><th scope="col">Cumulative (mSv)</th></tr></thead><tbody>{visible.map((sample) => <tr key={sample.day}><th scope="row">{sample.day}</th><td>{sample.dailyMicroSv}</td><td>{sample.cumulativeMilliSv}</td></tr>)}</tbody></table></div></details></section>;
}
