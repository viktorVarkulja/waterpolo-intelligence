"use client";

import { useFreshness } from "../lib/hooks";

function hoursAgo(timestamp: string | null) {
  if (!timestamp) return "--";
  const diffMs = Date.now() - new Date(timestamp).getTime();
  const hours = Math.max(0, Math.round(diffMs / 36e5));
  return `${hours}h ago`;
}

export default function FreshnessPill() {
  const { data } = useFreshness();
  const label = data?.last_import ? `Updated ${hoursAgo(data.last_import)}` : "No data";
  const tooltip = data
    ? `Last updated: ${data.last_import}\nTeams: ${data.team_count}\nMatches: ${data.match_count}\nStats rows: ${data.team_match_stat_count}`
    : "No freshness data";

  return (
    <div
      title={tooltip}
      className="rounded-full border border-slate/30 bg-white/70 px-3 py-1 text-xs text-slate"
    >
      {label}
    </div>
  );
}
