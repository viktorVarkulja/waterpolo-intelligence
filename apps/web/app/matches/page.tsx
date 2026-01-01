"use client";

import Link from "next/link";

import EmptyStateCard from "../../components/EmptyStateCard";
import { SkeletonCard } from "../../components/Skeletons";
import { useFilters } from "../../components/FilterProvider";
import { useMatches } from "../../lib/hooks";

export default function MatchesPage() {
  const { season, stage } = useFilters();
  const { data, isLoading } = useMatches({ season, stage });

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
        <p className="text-sm text-slate">Stage, date range, and close-game filters coming soon.</p>
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
