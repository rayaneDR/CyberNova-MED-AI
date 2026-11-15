"use client";
export default function ErrorScreen({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <div className="state-panel" role="alert"><h2>This screen could not be opened</h2><p>Try opening it again. No sensor data has been substituted.</p><button className="button primary" onClick={reset}>Try again</button></div>;
}
