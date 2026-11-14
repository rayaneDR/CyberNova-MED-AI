"use client";

import { useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TelemetrySample } from "@/lib/contracts";

const metrics = {
  heartRateBpm: { label: "Heart rate", unit: "bpm" },
  spo2Percent: { label: "SpO₂", unit: "%" },
  respiratoryRatePerMin: { label: "Respiratory rate", unit: "/min" },
} as const;
type Metric = keyof typeof metrics;

export function TelemetryChart({ samples }: { samples: TelemetrySample[] }) {
  const [metric, setMetric] = useState<Metric>("heartRateBpm");
  const selected = metrics[metric];
  const points = samples.map((sample) => ({
    ...sample,
    time: sample.timestamp.slice(11, 16),
  }));

  return (
    <section className="panel chart-panel" aria-labelledby="telemetry-heading">
      <div className="section-head">
        <div><h2 id="telemetry-heading">Telemetry window</h2><p>14 Nov 2026 · 08:00–08:55 UTC · Synthetic</p></div>
        <label className="metric-select">Signal
          <select value={metric} onChange={(event) => setMetric(event.target.value as Metric)}>
            {Object.entries(metrics).map(([key, value]) => <option key={key} value={key}>{value.label}</option>)}
          </select>
        </label>
      </div>
      <div className="chart" role="img" aria-label={`Synthetic ${selected.label} over 12 samples. Exact values in the table below.`}>
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart data={points} margin={{ top: 16, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid stroke="#dbe4ec" vertical={false} />
            <XAxis dataKey="time" tick={{ fill: "#526477", fontSize: 12 }} minTickGap={30} />
            <YAxis width={44} tick={{ fill: "#526477", fontSize: 12 }} domain={[0, "auto"]} />
            <Tooltip formatter={(value) => [`${value} ${selected.unit}`, selected.label]} />
            <Line type="linear" dataKey={metric} stroke="#1766ba" strokeWidth={3} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <details><summary>View {selected.label.toLowerCase()} data table</summary>
        <div className="table-scroll"><table><caption>Synthetic {selected.label} samples</caption>
          <thead><tr><th scope="col">Time (UTC)</th><th scope="col">{selected.label} ({selected.unit})</th></tr></thead>
          <tbody>{points.map((point) => <tr key={point.timestamp}><th scope="row">{point.time}</th><td>{point[metric] ?? "Unavailable"}</td></tr>)}</tbody>
        </table></div>
      </details>
    </section>
  );
}
