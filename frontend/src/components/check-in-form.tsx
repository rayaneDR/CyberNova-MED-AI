"use client";
import { useEffect, useState } from "react";
import type { CheckInInput, CheckInRecord } from "@/lib/contracts";
import { getCheckIns, submitCheckIn, validateCheckIn } from "@/lib/data-source";
import { getLiveCheckIns, submitLiveCheckIn } from "@/lib/api-client";
import type { DataMode } from "@/lib/contracts";
import { Check, ClipboardList } from "lucide-react";

export function CheckInForm({ subjectId, name, mode, missionId }: { subjectId: string; name: string; mode: DataMode; missionId: string }) {
  const [values, setValues] = useState({ sleepHours: "", fatigueScore: "", hydrationMl: "", notes: "" });
  const [errors, setErrors] = useState<Partial<Record<keyof CheckInInput, string>>>({});
  const [records, setRecords] = useState<CheckInRecord[]>([]);
  const [status, setStatus] = useState<"idle" | "saving" | "success">("idle");
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    Promise.resolve().then(() => {
      if (!active) return;
      try {
        if (mode === "demo") setRecords(getCheckIns(subjectId));
        else getLiveCheckIns(missionId, subjectId).then((items) => { if (active) setRecords(items); }).catch((cause: unknown) => { if (active) setError(cause instanceof Error ? cause.message : "Live check-in history could not be loaded."); });
      } catch { setError("Saved check-ins could not be loaded. Browser storage may be blocked or invalid; no records have been overwritten."); }
    });
    return () => { active = false; };
  }, [subjectId, mode, missionId]);
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const input: CheckInInput = { fatigueScale: "samn_perelli_1_7", sleepHours: values.sleepHours.trim() === "" ? NaN : Number(values.sleepHours), fatigueScore: values.fatigueScore === "" ? NaN : Number(values.fatigueScore), hydrationMl: values.hydrationMl.trim() === "" ? NaN : Number(values.hydrationMl), notes: values.notes };
    const validation = validateCheckIn(input);
    setErrors(validation); setError(""); setStatus("idle");
    if (Object.keys(validation).length) {
      const first = Object.keys(validation)[0];
      document.getElementById(first)?.focus();
      return;
    }
    setStatus("saving");
    try {
      const record = mode === "live" ? await submitLiveCheckIn(missionId, subjectId, input) : await submitCheckIn(subjectId, input);
      setRecords((previous) => [record, ...previous].slice(0, 30)); setStatus("success");
    } catch (cause) { setStatus("idle"); setError(cause instanceof Error ? cause.message : mode === "live" ? "The backend did not save your check-in. Keep your entries and retry." : "Your check-in was not saved. Browser storage may be unavailable; keep your entries and retry."); }
  }
  return <div className="two-column check-in-layout"><section className="panel"><div className="panel-heading"><div><h2>Daily crew report</h2><p>{name} · enter demonstration data only</p></div><ClipboardList size={22} className="accent" /></div><p className="help">Report sleep and fluid intake for the preceding 24 hours, and fatigue as you feel now. Form limits are input constraints, not health targets.</p><form onSubmit={handleSubmit} noValidate>
    <fieldset disabled={status === "saving"}><legend className="sr-only">Daily check-in measurements</legend><div className="form-grid">
      <label htmlFor="sleepHours">Sleep duration <span>hours / preceding 24h</span><input id="sleepHours" name="sleepHours" type="number" inputMode="decimal" min="0" max="24" step="0.1" required value={values.sleepHours} onChange={(event) => { setValues({ ...values, sleepHours: event.target.value }); setStatus("idle"); }} placeholder="e.g. 7.5" aria-invalid={!!errors.sleepHours} aria-describedby={errors.sleepHours ? "sleepHours-error" : undefined} />{errors.sleepHours && <small className="field-error" id="sleepHours-error">{errors.sleepHours}</small>}</label>
      <label htmlFor="fatigueScore">Fatigue score <span>Samn–Perelli · proposed MVP scale · 1–7</span><select id="fatigueScore" name="fatigueScore" required value={values.fatigueScore} onChange={(event) => { setValues({ ...values, fatigueScore: event.target.value }); setStatus("idle"); }} aria-invalid={!!errors.fatigueScore} aria-describedby={errors.fatigueScore ? "fatigueScore-error" : undefined}><option value="">Choose a score</option>{Array.from({ length: 7 }, (_, index) => <option key={index} value={index + 1}>{index + 1}</option>)}</select>{errors.fatigueScore && <small className="field-error" id="fatigueScore-error">{errors.fatigueScore}</small>}</label>
      <label htmlFor="hydrationMl">Hydration intake <span>mL / preceding 24h</span><input id="hydrationMl" name="hydrationMl" type="number" inputMode="decimal" min="0" max="10000" step="any" required value={values.hydrationMl} onChange={(event) => { setValues({ ...values, hydrationMl: event.target.value }); setStatus("idle"); }} placeholder="e.g. 1800" aria-invalid={!!errors.hydrationMl} aria-describedby={errors.hydrationMl ? "hydrationMl-error" : "hydration-help"} /><small id="hydration-help">Self-reported intake, not the fixture hydration index.</small>{errors.hydrationMl && <small className="field-error" id="hydrationMl-error">{errors.hydrationMl}</small>}</label>
      <label htmlFor="notes" className="full-width">Notes <span>optional / {values.notes.length} of 500 characters</span><textarea id="notes" name="notes" rows={4} maxLength={500} value={values.notes} onChange={(event) => { setValues({ ...values, notes: event.target.value }); setStatus("idle"); }} placeholder="Activity, rest, or sensor context. Use fictional information only." aria-invalid={!!errors.notes} />{errors.notes && <small className="field-error">{errors.notes}</small>}</label>
    </div><div className="form-actions"><button className="button primary" type="submit">{status === "saving" ? mode === "live" ? "Sending to backend…" : "Saving check-in…" : mode === "live" ? "Submit live API check-in" : "Save demo check-in"}</button><span>{mode === "live" ? "POST /checkins · persisted in SQLite" : "Saved in this browser only"}</span></div></fieldset>
    <p className="help">Fatigue anchors: 1 = fully alert; 7 = completely exhausted. <a className="text-link" href="https://ntrs.nasa.gov/citations/20130001718" target="_blank" rel="noreferrer">Scale reference (new tab)</a>. This project proposes the scale; no NASA mandate is claimed.</p>
    {error && <p className="error-message" role="alert">{error}</p>}{status === "success" && <p className="success-message" role="status"><Check size={18} />Check-in saved for {name}. The recorded sensor session is unchanged.</p>}
  </form></section><section className="panel"><div className="panel-heading"><div><h2>Check-in history</h2><p>{mode === "live" ? "GET /checkins · backend history" : "Local mock adapter · latest 30 entries"}</p></div><span className="badge">{records.length} saved</span></div>{records.length === 0 ? <div className="inline-empty"><ClipboardList size={30} /><h3>No check-ins yet</h3><p>Your first saved report will appear here.</p></div> : <div className="check-in-history">{records.map((record) => <article key={record.id}><time dateTime={record.submittedAt}>{record.submittedAt.slice(0, 16).replace("T", " ")} UTC</time><dl className="mini-stats"><div><dt>Sleep</dt><dd>{record.sleepHours} h</dd></div><div><dt>Fatigue</dt><dd>{record.fatigueScore}/{record.fatigueScale === "samn_perelli_1_7" ? 7 : 10}</dd></div><div><dt>Intake</dt><dd>{record.hydrationMl} mL</dd></div></dl>{record.notes && <p className="user-notes">{record.notes}</p>}<span className="subtle">{record.fatigueScale === "samn_perelli_1_7" ? "Samn–Perelli 1–7" : "Legacy demo 1–10 · not converted"} · {record.source === "api" ? "synthetic backend record" : "browser-local demonstration"}</span></article>)}</div>}<p className="help">{mode === "live" ? "Live history is reloaded from the backend and persists in SQLite. Only synthetic demonstration reports should be entered." : "Entries persist on this device after reload. They are not sent to a backend, NASA, or another crew member. Do not enter real health information."}</p></section></div>;
}
