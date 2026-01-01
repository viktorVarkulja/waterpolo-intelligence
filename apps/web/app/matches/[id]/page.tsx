"use client";

import { useParams } from "next/navigation";

import EmptyStateCard from "../../../components/EmptyStateCard";
import { SkeletonChart } from "../../../components/Skeletons";
import { useMatch } from "../../../lib/hooks";

export default function MatchDetailPage() {
  const params = useParams<{ id: string }>();
  const matchId = params?.id;
  const { data, isLoading } = useMatch(matchId as string);

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
        <p className="text-sm text-slate">{data.stage || "Stage"} · {data.date || "TBD"} · {data.venue || "Venue"}</p>
      </div>
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Team stats comparison</h3>
        <p className="text-sm text-slate">Box score and player lines will populate once player stats are ingested.</p>
      </div>
    </section>
  );
}
