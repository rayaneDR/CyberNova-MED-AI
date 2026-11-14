import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CyberNova MED AI | Crew overview",
  description: "CyberNova X synthetic crew telemetry demo for NASA Space Apps Challenge Meknes 2026. No medical diagnosis or treatment advice.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
