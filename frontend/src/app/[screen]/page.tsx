import { notFound } from "next/navigation";
import { MissionScreen } from "@/components/mission-screen";
import type { Screen } from "@/lib/contracts";
const screens = ["health", "alerts", "check-in", "radiation", "research"] as const;
export function generateStaticParams() { return screens.map((screen) => ({ screen })); }
export const dynamicParams = false;
export default async function ScreenPage({ params }: { params: Promise<{ screen: string }> }) {
  const { screen } = await params;
  if (!screens.some((value) => value === screen)) notFound();
  return <MissionScreen screen={screen as Screen} />;
}
