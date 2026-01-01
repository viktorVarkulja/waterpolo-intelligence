"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import EmptyStateCard from "../../components/EmptyStateCard";
import { SkeletonCard } from "../../components/Skeletons";
import { useFilters } from "../../components/FilterProvider";
import { useMatches, useTeams } from "../../lib/hooks";

export default function MatchesPage() {
  const { season, stage } = useFilters();
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const teamParam = searchParams.get("team") || "";
  const fromDate = searchParams.get("from") || "";
  const toDate = searchParams.get("to") || "";
  const close = searchParams.get("close") === "true";
  const teamId = teamParam ? Number(teamParam) : null;
  const { data, isLoading } = useMatches({
    season,
    stage,
    team: teamId,
    from: fromDate,
    to: toDate,
    close: close ? "true" : ""
  });
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
      <div className="grid gap-4 md:grid-cols-2">
        {Array.from({ length: 4 }).map((_, idx) => (
          <SkeletonCard key={idx} />
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <EmptyStateCard
        title="No matches"
        description="Match data will appear once scraping is complete."
        actionLabel="Scrape matches"
        actionHref="/admin"
      />
    );
  }

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Matches</h2>
        <p className="text-sm text-slate">Filter by team, dates, and close games.</p>
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
        <label className="text-xs uppercase tracking-wide text-slate">From</label>
        <input
          type="date"
          className="rounded-full border border-slate/30 bg-white/80 px-3 py-2 text-sm"
          value={fromDate}
          onChange={(event) => updateParam("from", event.target.value)}
        />
        <label className="text-xs uppercase tracking-wide text-slate">To</label>
        <input
          type="date"
          className="rounded-full border border-slate/30 bg-white/80 px-3 py-2 text-sm"
          value={toDate}
          onChange={(event) => updateParam("to", event.target.value)}
        />
        <label className="flex items-center gap-2 text-xs uppercase tracking-wide text-slate">
          <input
            type="checkbox"
            checked={close}
            onChange={(event) => updateParam("close", event.target.checked ? "true" : "")}
          />
          Close games
        </label>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {data.map((match) => (
          <Link
            key={match.id}
            href={`/matches/${match.id}`}
            className="rounded-2xl border border-white bg-white/80 p-5 shadow-sm"
          >
            <div className="flex items-center justify-between text-sm text-slate">
              <span>{match.stage || "Stage"}</span>
              <span>{match.date || "TBD"}</span>
            </div>
            <div className="mt-3 text-lg font-semibold">
              {match.home_team} {match.home_score ?? "-"} — {match.away_score ?? "-"} {match.away_team}
            </div>
            <p className="mt-2 text-xs text-slate">{match.venue || "Venue TBD"}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
