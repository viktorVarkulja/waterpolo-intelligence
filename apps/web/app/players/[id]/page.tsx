"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { LineChart } from "../../../components/Charts";
import EmptyStateCard from "../../../components/EmptyStateCard";
import KpiCard from "../../../components/KpiCard";
import { SkeletonChart } from "../../../components/Skeletons";
import { usePlayer } from "../../../lib/hooks";

export default function PlayerProfile() {
  const params = useParams<{ id: string }>();
  const playerId = Number(params?.id);
  const { data: player, isLoading } = usePlayer(playerId);

  if (isLoading) return <SkeletonChart />;
  if (!player) {
    return <EmptyStateCard title="Player not found" description="Check the roster ingestion or try again." />;
  }

  const hasStats = Boolean(player.stats);

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <h2 className="text-3xl font-semibold">{player.name}</h2>
        <p className="text-sm text-slate">
          {player.team_name || "Team TBD"} · #{player.number ?? "-"} · {player.position ?? "Role TBD"}
        </p>
      </div>

      {!hasStats ? (
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <EmptyStateCard
            title="Roster-only mode"
            description="Player match stats are not available yet. We will surface trends and efficiency once match line data is ingested."
            actionLabel="View teams"
            actionHref="/teams"
          />
          <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
            <h3 className="text-lg font-semibold">What will appear here</h3>
            <ul className="mt-3 text-sm text-slate space-y-2">
              <li>Rolling goals + shots trend</li>
              <li>Efficiency breakdown by situation</li>
              <li>Match log with impact metrics</li>
            </ul>
          </div>
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <KpiCard label="Goals/Match" value={player.stats?.goals ?? 0} delta={0.4} />
            <KpiCard label="Shooting %" value={`${player.stats?.shooting_pct ?? 0}%`} delta={1.2} />
            <KpiCard label="Assists" value={player.stats?.assists ?? 0} delta={-0.3} />
          </div>
          <LineChart
            title="Recent form"
            caption="Rolling goals and shots"
            categories={["M1", "M2", "M3", "M4", "M5"]}
            series={[
              { name: "Goals", data: [2, 1, 3, 1, 2], color: "#0ea5a3" },
              { name: "Shots", data: [4, 3, 6, 4, 5], color: "#f97316" }
            ]}
          />
        </>
      )}
    </section>
  );
}
