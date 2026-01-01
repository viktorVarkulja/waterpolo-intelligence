"use client";

import { useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { LineChart } from "../../components/Charts";
import EmptyStateCard from "../../components/EmptyStateCard";
import { useFilters } from "../../components/FilterProvider";
import { useCompare, useTeams } from "../../lib/hooks";

export default function ComparePage() {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const { season, stage } = useFilters();
  const teamA = params.get("teamA");
  const teamB = params.get("teamB");
  const window = params.get("window") || "5";

  const { data: teams } = useTeams({});
  const { data, isLoading } = useCompare({ teamA, teamB, window, season, stage });

  const trendCategories = useMemo(() => ["M1", "M2", "M3", "M4", "M5"], []);

  function updateParam(key: string, value: string) {
    const query = new URLSearchParams(params.toString());
    if (value) {
      query.set(key, value);
    } else {
      query.delete(key);
    }
    router.push(`${pathname}?${query.toString()}`);
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
        <h2 className="text-2xl font-semibold">Compare matchups</h2>
        <p className="text-sm text-slate">Shareable deep links keep filters intact.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto_1fr_auto]">
          <select
            className="rounded-lg border border-slate/30 px-3 py-2 text-sm"
            value={teamA || ""}
            onChange={(event) => updateParam("teamA", event.target.value)}
          >
            <option value="">Select Team A</option>
            {teams?.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </select>
          <button
            className="rounded-lg border border-slate/30 px-3 py-2 text-sm"
            onClick={() => {
              updateParam("teamA", teamB || "");
              updateParam("teamB", teamA || "");
            }}
          >
            Swap
          </button>
          <select
            className="rounded-lg border border-slate/30 px-3 py-2 text-sm"
            value={teamB || ""}
            onChange={(event) => updateParam("teamB", event.target.value)}
          >
            <option value="">Select Team B</option>
            {teams?.map((team) => (
              <option key={team.id} value={team.id}>
                {team.name}
              </option>
            ))}
          </select>
          <button
            className="rounded-lg border border-slate/30 px-3 py-2 text-sm"
            onClick={() => navigator.clipboard.writeText(window.location.href)}
          >
            Copy link
          </button>
        </div>
        <div className="mt-3 flex gap-2">
          {[5, 10, 15].map((val) => (
            <button
              key={val}
              onClick={() => updateParam("window", String(val))}
              className={`rounded-full border px-3 py-1 text-xs ${window === String(val) ? "border-ink text-ink" : "border-slate/30"}`}
            >
              {val}-match window
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">Loading...</div>
      ) : !data ? (
        <EmptyStateCard
          title="Choose two teams"
          description="Pick Team A and Team B to unlock comparison insights."
        />
      ) : (
        <>
          <div className="grid gap-4 lg:grid-cols-[1fr_auto_1fr]">
            <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
              <h3 className="text-lg font-semibold">{data.team_a.name}</h3>
              <p className="text-sm text-slate">Goals/Match: {data.team_a.aggregates.goals_per_match.toFixed(2)}</p>
            </div>
            <div className="rounded-2xl border border-white bg-white/80 p-6 text-center text-sm text-slate shadow-sm">
              {Object.entries(data.deltas)
                .slice(0, 5)
                .map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between gap-4">
                    <span>{key.replace(/_/g, " ")}</span>
                    <span className={value >= 0 ? "text-wave" : "text-coral"}>
                      {value >= 0 ? "▲" : "▼"} {value.toFixed(2)}
                    </span>
                  </div>
                ))}
            </div>
            <div className="rounded-2xl border border-white bg-white/80 p-6 shadow-sm">
              <h3 className="text-lg font-semibold">{data.team_b.name}</h3>
              <p className="text-sm text-slate">Goals/Match: {data.team_b.aggregates.goals_per_match.toFixed(2)}</p>
            </div>
          </div>

          <LineChart
            title="Trend overlay"
            caption="Rolling goal output for both teams"
            categories={trendCategories}
            series={[
              { name: data.team_a.name, data: [8, 10, 12, 9, 11], color: "#0ea5a3" },
              { name: data.team_b.name, data: [9, 7, 11, 8, 10], color: "#f97316" }
            ]}
          />
        </>
      )}
    </section>
  );
}
