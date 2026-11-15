"use client";
import { useState } from "react";
import Link from "next/link";
import { ArrowUpRight, Pause, Play } from "lucide-react";

/** Decorative orbital illustration; no measured orbital data. */
export function OrbitalIntro() {
 const [paused, setPaused] = useState(false);
 return <section className={`orbital-intro ${paused ? "motion-paused" : ""}`} aria-label="Mission workspace introduction">
  <div className="orbital-copy"><span className="orbital-eyebrow">CYBERNOVA X / HUMAN SPACEFLIGHT</span><h2>Every signal.<br /><em>In context.</em></h2><p>A clearer view of crew observations, from source quality to the patterns that deserve a closer look.</p><Link className="orbital-cta" href="/health">Explore health monitoring <ArrowUpRight size={18} /></Link><span className="orbital-caption">Fictional mission · synthetic telemetry · human review</span></div>
  <div className="orbital-scene" aria-hidden="true"><div className="orbit-track orbit-back" /><div className="orbital-globe"><div className="globe-grid" /><div className="globe-shade" /></div><div className="orbit-track orbit-front"><span className="orbit-craft" /></div><div className="orbit-coordinate">ILLUSTRATIVE ORBIT / NO LIVE POSITION</div></div>
  <button className="motion-toggle" aria-pressed={paused} onClick={() => setPaused(!paused)} aria-label={paused ? "Resume orbital animation" : "Pause orbital animation"}>{paused ? <Play size={14} /> : <Pause size={14} />}<span>{paused ? "Resume motion" : "Pause motion"}</span></button>
 </section>;
}
