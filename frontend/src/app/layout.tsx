import type { Metadata } from "next";
import "./globals.css";
import { MissionProvider } from "@/components/mission-provider";
import { MissionShell } from "@/components/mission-shell";

export const metadata: Metadata = {
  title: "CyberNova MED AI | Mission control",
  description: "CyberNova X synthetic crew telemetry demo for NASA Space Apps Challenge Meknes 2026. No medical diagnosis or treatment advice.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><MissionProvider><MissionShell>{children}</MissionShell></MissionProvider></body></html>;
}
