"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { RadarChart, LineChart } from "../../../components/Charts";
import FormDots from "../../../components/FormDots";
import KpiCard from "../../../components/KpiCard";
import { SkeletonChart } from "../../../components/Skeletons";
import EmptyStateCard from "../../../components/EmptyStateCard";
import { useFilters } from "../../../components/FilterProvider";
import { useTeam, useTeamTrends } from "../../../lib/hooks";

const tabs = ["Overview", "Trends", "Efficiency", "Discipline", "Head-to-head", "Roster"] as const;

export default function TeamDashboard() {
  const { season, stage } = useFilters();
  const params = useParams<{ slug: string }>();
  const slug = params?.slug as string;
  const { data: team, isLoading } = useTeam(slug, true);
  const teamId = team?.id ?? 0;
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>("Overview");
  const { data: trends } = useTeamTrends(teamId, { season, stage, window: 5 });

  const trendSeries = useMemo(() => {
    if (!trends?.points) return { categories: [], goals: [], shots: [] };
    return {
      categories: trends.points.map((p) => `M${p.match_index}`),
      goals: trends.points.map((p) => p.goals),
      shots: trends.points.map((p) => p.shots)
    };
  }, [trends]);

  if (isLoading || !team) {
    return <SkeletonChart />;
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate">Team Dashboard</p>
            <h2 className="text-3xl font-semibold">{team.name}</h2>
            <div className="mt-3 flex items-center gap-3">
              <FormDots results={team.form || [1, 1, -1, 0, 1, 1, 0, -1, 1, 1]} />
              <span className="text-xs text-slate">last 10</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="rounded-full border border-slate/30 px-4 py-2 text-xs">Pin</button>
            <Link href={`/compare?teamA=${team.id}`} className="rounded-full bg-wave px-4 py-2 text-xs text-white">
              Compare
            </Link>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <KpiCard label="Goals/Match" value={team.aggregates.goals_per_match.toFixed(2)} delta={0.4} trend={trendSeries.goals.slice(-8)} />
        <KpiCard label="Shooting %" value={`${(team.aggregates.shooting_pct * 100).toFixed(1)}%`} delta={1.2} trend={trendSeries.shots.slice(-8)} />
        <KpiCard label="Extra-man %" value={`${(team.aggregates.extra_man_pct * 100).toFixed(1)}%`} delta={-0.6} trend={trendSeries.goals.slice(-8)} />
      </div>

      <div className="flex flex-wrap gap-3">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-full px-4 py-2 text-xs ${
              activeTab === tab ? "bg-ink text-white" : "border border-slate/30 text-slate"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === "Overview" ? (
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          {trends?.points?.length ? (
            <LineChart
              title="Form index"
              caption="Rolling goals and shot volume"
              categories={trendSeries.categories}
              series={[
                { name: "Goals", data: trendSeries.goals, color: "#0ea5a3" },
                { name: "Shots", data: trendSeries.shots, color: "#f97316" }
              ]}
            />
          ) : (
            <EmptyStateCard
              title="No trend data yet"
              description="Scrape match stats to unlock rolling form charts."
              actionLabel="Scrape data"
              actionHref="/admin"
            />
          )}
          <RadarChart
            title="Team profile"
            caption="Shot quality, discipline, and pace mix"
            indicators={["Shooting", "Extra-man", "Center", "Counter", "Discipline"]}
            values={[
              team.aggregates.shooting_pct * 100,
              team.aggregates.extra_man_pct * 100,
              team.aggregates.center_pct * 100,
              team.aggregates.counter_pct * 100,
              100 - team.aggregates.turnovers_per_match
            ]}
          />
        </div>
      ) : (
        <EmptyStateCard
          title="Section coming online"
          description="This tab will populate once we ingest richer match and roster data."
          actionLabel="Back to overview"
          actionHref={`/teams/${team.slug}`}
        />
      )}
    </section>
  );
}
