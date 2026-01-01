"use client";

import { useMemo } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import EmptyStateCard from "../../../components/EmptyStateCard";
import { SkeletonChart } from "../../../components/Skeletons";
import { useMatch } from "../../../lib/hooks";

export default function MatchDetailPage() {
  const params = useParams<{ id: string }>();
  const matchId = params?.id;
  const { data, isLoading } = useMatch(matchId as string);

  const homeStats = useMemo(() => data?.team_stats.find((team) => team.is_home), [data]);
  const awayStats = useMemo(() => data?.team_stats.find((team) => !team.is_home), [data]);

  const statRows = useMemo(() => {
    if (!homeStats || !awayStats) return [];
    const rows = [
      { label: "Goals", key: "goals" },
      { label: "Shots", key: "shots" },
      { label: "Shooting %", key: "shooting_pct", format: "pct" },
      { label: "Extra-man", key: "extra_man_pct", format: "pct" },
      { label: "Center", key: "center_goals", keyAlt: "center_shots" },
      { label: "Counter", key: "counter_goals", keyAlt: "counter_shots" },
      { label: "Assists", key: "assists" },
      { label: "Turnovers", key: "turnovers" },
      { label: "Steals", key: "steals" },
      { label: "Blocks", key: "blocks" },
      { label: "Sprints", key: "sprints_won", keyAlt: "sprints" },
      { label: "Exclusions drawn", key: "exclusions_drawn" },
      { label: "Exclusions fouls", key: "exclusions_fouls" }
    ];

    return rows.map((row) => {
      const homeVal = homeStats.stats[row.key];
      const awayVal = awayStats.stats[row.key];
      const homeAlt = row.keyAlt ? homeStats.stats[row.keyAlt] : undefined;
      const awayAlt = row.keyAlt ? awayStats.stats[row.keyAlt] : undefined;
      const format = row.format;

      const formatValue = (value: number | undefined, alt?: number) => {
        if (format === "pct") {
          const pct = value ? value * 100 : 0;
          return `${pct.toFixed(1)}%`;
        }
        if (typeof alt === "number") {
          return `${value ?? 0}/${alt}`;
        }
        return value ?? 0;
      };

      return {
        label: row.label,
        home: formatValue(homeVal, homeAlt),
        away: formatValue(awayVal, awayAlt)
      };
    });
  }, [homeStats, awayStats]);

  const playerGroups = useMemo(() => {
    const groups = {
      home: [] as typeof data.player_stats,
      away: [] as typeof data.player_stats
    };
    const seenHome = new Set<number>();
    const seenAway = new Set<number>();
    data?.player_stats.forEach((line) => {
      if (line.team_id === data.home_team_id) {
        if (seenHome.has(line.player_id)) return;
        seenHome.add(line.player_id);
        groups.home.push(line);
      } else if (line.team_id === data.away_team_id) {
        if (seenAway.has(line.player_id)) return;
        seenAway.add(line.player_id);
        groups.away.push(line);
      }
    });
    return groups;
  }, [data]);

  if (isLoading) return <SkeletonChart />;
  if (!data) {
    return <EmptyStateCard title="Match not found" description="The match data is not available yet." />;
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <h2 className="text-2xl font-semibold">
          {data.home_team} {data.home_score ?? "-"} — {data.away_score ?? "-"} {data.away_team}
        </h2>
        <p className="text-sm text-slate">
          {data.stage || "Stage"} · {data.date || "TBD"} · {data.venue || "Venue"}
        </p>
      </div>
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Team stats comparison</h3>
          <Link href="/teams" className="text-xs text-wave">
            View teams
          </Link>
        </div>
        {!homeStats || !awayStats ? (
          <p className="text-sm text-slate">Team match stats are not available yet.</p>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-xs uppercase text-slate">
                <tr>
                  <th className="py-2 text-left">Stat</th>
                  <th className="py-2 text-right">{data.home_team}</th>
                  <th className="py-2 text-right">{data.away_team}</th>
                </tr>
              </thead>
              <tbody>
                {statRows.map((row) => (
                  <tr key={row.label} className="border-t border-slate-100">
                    <td className="py-2 text-left">{row.label}</td>
                    <td className="py-2 text-right font-medium text-ink">{row.home}</td>
                    <td className="py-2 text-right font-medium text-ink">{row.away}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Player box score</h3>
        {data.player_stats.length === 0 ? (
          <p className="text-sm text-slate">Player lines will appear once player match stats are ingested.</p>
        ) : (
          <div className="mt-4 grid gap-6 lg:grid-cols-2">
            {[{ label: data.home_team, rows: playerGroups.home }, { label: data.away_team, rows: playerGroups.away }].map(
              (group) => (
                <div key={group.label}>
                  <p className="text-xs uppercase text-slate">{group.label}</p>
                  <div className="mt-2 overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="text-xs uppercase text-slate">
                        <tr>
                          <th className="py-2 text-left">Player</th>
                          <th className="py-2 text-right">G</th>
                          <th className="py-2 text-right">S</th>
                          <th className="py-2 text-right">A</th>
                          <th className="py-2 text-right">St</th>
                          <th className="py-2 text-right">Bl</th>
                          <th className="py-2 text-right">Ex</th>
                          <th className="py-2 text-right">To</th>
                        </tr>
                      </thead>
                      <tbody>
                        {group.rows.map((line, idx) => (
                          <tr key={`${line.player_id}-${line.team_id ?? "na"}-${idx}`} className="border-t border-slate-100">
                            <td className="py-2 text-left">{line.player_name}</td>
                            <td className="py-2 text-right">{line.goals ?? 0}</td>
                            <td className="py-2 text-right">{line.shots ?? 0}</td>
                            <td className="py-2 text-right">{line.assists ?? 0}</td>
                            <td className="py-2 text-right">{line.steals ?? 0}</td>
                            <td className="py-2 text-right">{line.blocks ?? 0}</td>
                            <td className="py-2 text-right">{line.exclusions ?? 0}</td>
                            <td className="py-2 text-right">{line.turnovers ?? 0}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )
            )}
          </div>
        )}
      </div>
    </section>
  );
}
