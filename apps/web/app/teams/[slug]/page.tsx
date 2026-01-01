"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { RadarChart, LineChart, ScatterChart, DistributionChart } from "../../../components/Charts";
import FormDots from "../../../components/FormDots";
import KpiCard from "../../../components/KpiCard";
import { SkeletonChart } from "../../../components/Skeletons";
import EmptyStateCard from "../../../components/EmptyStateCard";
import { useFilters } from "../../../components/FilterProvider";
import { useTeam, useTeamMatches, useTeamRoster, useTeamTrends, useTeams } from "../../../lib/hooks";

const tabs = ["Overview", "Trends", "Efficiency", "Discipline", "Head-to-head", "Roster"] as const;

export default function TeamDashboard() {
  const { season, stage } = useFilters();
  const params = useParams<{ slug: string }>();
  const slug = params?.slug as string;
  const { data: team, isLoading } = useTeam(slug, true);
  const teamId = team?.id ?? 0;
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>("Overview");
  const [opponentFilter, setOpponentFilter] = useState<string>("");
  const { data: trends } = useTeamTrends(teamId, { season, stage, window: 5 });
  const { data: matches } = useTeamMatches(teamId, { season, stage });
  const { data: roster } = useTeamRoster(teamId, { season });
  const { data: allTeams } = useTeams({ season, stage });

  const trendSeries = useMemo(() => {
    if (!trends?.points) return { categories: [], goals: [], shots: [] };
    return {
      categories: trends.points.map((p) => `M${p.match_index}`),
      goals: trends.points.map((p) => p.goals),
      shots: trends.points.map((p) => p.shots)
    };
  }, [trends]);

  const matchSeries = useMemo(() => {
    if (!matches?.length) return { categories: [], team: [], opponent: [] };
    return {
      categories: matches.map((_, idx) => `M${idx + 1}`),
      team: matches.map((match) => match.team_score ?? 0),
      opponent: matches.map((match) => match.opponent_score ?? 0)
    };
  }, [matches]);

  const shootingPctSeries = useMemo(() => {
    if (!trends?.points) return [];
    return trends.points.map((p) => (p.shots ? Math.round((p.goals / p.shots) * 1000) / 10 : 0));
  }, [trends]);

  const efficiencyPoints = useMemo(() => {
    if (!trends?.points) return [];
    return trends.points.map((p) => [p.shots, p.goals] as [number, number]);
  }, [trends]);

  const opponentOptions = useMemo(() => {
    if (!matches?.length) return [];
    return Array.from(new Set(matches.map((match) => match.opponent))).sort();
  }, [matches]);

  const h2hMatches = useMemo(() => {
    if (!matches?.length) return [];
    if (!opponentFilter) return matches;
    return matches.filter((match) => match.opponent === opponentFilter);
  }, [matches, opponentFilter]);

  const h2hSummary = useMemo(() => {
    if (!h2hMatches.length) {
      return { wins: 0, losses: 0, draws: 0, goalsFor: 0, goalsAgainst: 0 };
    }
    return h2hMatches.reduce(
      (acc, match) => {
        const teamScore = match.team_score ?? 0;
        const oppScore = match.opponent_score ?? 0;
        if (teamScore > oppScore) acc.wins += 1;
        else if (teamScore < oppScore) acc.losses += 1;
        else acc.draws += 1;
        acc.goalsFor += teamScore;
        acc.goalsAgainst += oppScore;
        return acc;
      },
      { wins: 0, losses: 0, draws: 0, goalsFor: 0, goalsAgainst: 0 }
    );
  }, [h2hMatches]);

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
      ) : null}

      {activeTab === "Trends" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {trends?.points?.length ? (
            <>
              <LineChart
                title="Goals + shots"
                caption="Rolling goals and shot volume"
                categories={trendSeries.categories}
                series={[
                  { name: "Goals", data: trendSeries.goals, color: "#0ea5a3" },
                  { name: "Shots", data: trendSeries.shots, color: "#f97316" }
                ]}
              />
              <LineChart
                title="Shooting %"
                caption="Rolling efficiency from shots to goals"
                categories={trendSeries.categories}
                series={[{ name: "Shooting %", data: shootingPctSeries, color: "#2563eb" }]}
              />
            </>
          ) : (
            <EmptyStateCard
              title="No trend data yet"
              description="Scrape match stats to unlock rolling trend charts."
              actionLabel="Scrape data"
              actionHref="/admin"
            />
          )}
          {matches?.length ? (
            <LineChart
              title="Goals for vs against"
              caption="Match-level scorelines"
              categories={matchSeries.categories}
              series={[
                { name: "Goals for", data: matchSeries.team, color: "#0ea5a3" },
                { name: "Goals against", data: matchSeries.opponent, color: "#ef4444" }
              ]}
            />
          ) : (
            <EmptyStateCard title="No matches yet" description="Match results will appear after scraping." />
          )}
        </div>
      ) : null}

      {activeTab === "Efficiency" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {efficiencyPoints.length ? (
            <ScatterChart
              title="Shots vs goals"
              caption="Each point is a rolling window"
              points={efficiencyPoints}
            />
          ) : (
            <EmptyStateCard title="No efficiency data" description="Scrape match stats to unlock efficiency charts." />
          )}
          {shootingPctSeries.length ? (
            <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
              <h3 className="text-sm font-semibold">Best + worst windows</h3>
              <p className="text-xs text-slate mb-4">Rolling shooting % extremes.</p>
              <div className="grid gap-3 text-sm text-slate">
                <div className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                  <span>Best window</span>
                  <span className="font-semibold text-ink">
                    {Math.max(...shootingPctSeries).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                  <span>Worst window</span>
                  <span className="font-semibold text-ink">
                    {Math.min(...shootingPctSeries).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <EmptyStateCard title="No efficiency windows" description="Match stats will populate these windows." />
          )}
        </div>
      ) : null}

      {activeTab === "Discipline" ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <DistributionChart
            title="Possession discipline"
            caption="Turnovers and steals per match"
            categories={["Turnovers", "Steals"]}
            values={[team.aggregates.turnovers_per_match, team.aggregates.steals_per_match]}
          />
          <div className="grid gap-4">
            <KpiCard
              label="Turnovers/Match"
              value={team.aggregates.turnovers_per_match.toFixed(2)}
              delta={0}
            />
            <KpiCard
              label="Steals/Match"
              value={team.aggregates.steals_per_match.toFixed(2)}
              delta={0}
            />
            <KpiCard
              label="Sprints won %"
              value={`${(team.aggregates.sprints_win_pct * 100).toFixed(1)}%`}
              delta={0}
            />
          </div>
        </div>
      ) : null}

      {activeTab === "Head-to-head" ? (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <label className="text-xs uppercase tracking-wide text-slate">Opponent</label>
            <select
              className="rounded-full border border-slate/30 bg-white/80 px-3 py-2 text-sm"
              value={opponentFilter}
              onChange={(event) => setOpponentFilter(event.target.value)}
            >
              <option value="">All opponents</option>
              {opponentOptions.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
            {allTeams?.length ? (
              <span className="text-xs text-slate">{allTeams.length} teams tracked</span>
            ) : null}
          </div>
          {h2hMatches.length ? (
            <>
              <div className="grid gap-4 md:grid-cols-4">
                <KpiCard label="Wins" value={h2hSummary.wins} delta={0} />
                <KpiCard label="Losses" value={h2hSummary.losses} delta={0} />
                <KpiCard label="Draws" value={h2hSummary.draws} delta={0} />
                <KpiCard
                  label="Goal diff"
                  value={h2hSummary.goalsFor - h2hSummary.goalsAgainst}
                  delta={0}
                />
              </div>
              <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
                <h3 className="text-sm font-semibold">Match log</h3>
                <p className="text-xs text-slate mb-4">Recent head-to-head results.</p>
                <div className="grid gap-3 text-sm text-slate">
                  {h2hMatches.map((match) => (
                    <div key={match.match_id} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                      <span>{match.opponent}</span>
                      <span className="text-xs text-slate">
                        {match.home ? "Home" : "Away"} · {match.stage || "Stage"}
                      </span>
                      <span className="font-semibold text-ink">
                        {match.team_score ?? "-"}:{match.opponent_score ?? "-"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <EmptyStateCard title="No head-to-head data" description="No matches found for this opponent." />
          )}
        </div>
      ) : null}

      {activeTab === "Roster" ? (
        roster?.length ? (
          <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
            <h3 className="text-sm font-semibold">Roster</h3>
            <p className="text-xs text-slate mb-4">Player directory for this team.</p>
            <div className="grid gap-2 text-sm text-slate">
              {roster.map((player) => (
                <div key={player.id} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3">
                  <span className="font-medium text-ink">{player.name}</span>
                  <span className="text-xs text-slate">#{player.number ?? "-"}</span>
                  <span className="text-xs text-slate">{player.position ?? "Role TBD"}</span>
                  <Link href={`/players/${player.id}`} className="text-xs text-wave">
                    View
                  </Link>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <EmptyStateCard
            title="No roster data yet"
            description="Scrape rosters to populate player lists."
            actionLabel="Scrape rosters"
            actionHref="/admin"
          />
        )
      ) : null}
    </section>
  );
}
