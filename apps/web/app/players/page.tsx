"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import EmptyStateCard from "../../components/EmptyStateCard";
import { SkeletonCard } from "../../components/Skeletons";
import { useFilters } from "../../components/FilterProvider";
import { usePlayers, useTeams } from "../../lib/hooks";

export default function PlayersPage() {
  const { season, stage, q } = useFilters();
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const teamParam = searchParams.get("team") || "";
  const teamId = teamParam ? Number(teamParam) : null;
  const { data, isLoading } = usePlayers({ season, stage, q, team: teamId });
  const { data: teams } = useTeams({ season, stage });

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname);
  };

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, idx) => (
          <SkeletonCard key={idx} />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <EmptyStateCard
        title="No roster data"
        description="Rosters will appear once scraped. Player analytics unlock after match stats ingestion."
        actionLabel="Scrape rosters"
        actionHref="/admin"
      />
    );
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Players</h2>
        <p className="text-sm text-slate">Roster directory and upcoming analytics.</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-xs uppercase tracking-wide text-slate">Team</label>
        <select
          className="rounded-full border border-slate/30 bg-white/80 px-3 py-2 text-sm"
          value={teamParam}
          onChange={(event) => updateParam("team", event.target.value)}
        >
          <option value="">All teams</option>
          {teams?.map((team) => (
            <option key={team.id} value={team.id}>
              {team.name}
            </option>
          ))}
        </select>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data.map((player) => (
          <div key={player.id} className="rounded-2xl border border-white bg-white/80 p-5 shadow-sm">
            <h3 className="text-lg font-semibold">{player.name}</h3>
            <p className="text-sm text-slate">{player.team_name || "Team TBD"}</p>
            <div className="mt-3 flex items-center gap-3 text-xs text-slate">
              <span>#{player.number ?? "-"}</span>
              <span>{player.position ?? "Role TBD"}</span>
            </div>
            {player.stats?.matches ? (
              <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate">
                <span className="rounded-full bg-slate-100 px-2 py-1">
                  {player.stats.goals_per_match.toFixed(2)} G/Match
                </span>
                <span className="rounded-full bg-slate-100 px-2 py-1">
                  {(player.stats.shooting_pct * 100).toFixed(1)}% Shooting
                </span>
              </div>
            ) : null}
            <div className="mt-4 flex items-center gap-2">
              <Link href={`/players/${player.id}`} className="rounded-full border border-slate/30 px-3 py-1 text-xs">
                View
              </Link>
              <button className="rounded-full border border-slate/30 px-3 py-1 text-xs">Pin</button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
