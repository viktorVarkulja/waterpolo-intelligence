"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import FormDots from "../../components/FormDots";
import KpiCard from "../../components/KpiCard";
import { DistributionChart } from "../../components/Charts";
import EmptyStateCard from "../../components/EmptyStateCard";
import { SkeletonCard } from "../../components/Skeletons";
import { useFilters } from "../../components/FilterProvider";
import { useTeams } from "../../lib/hooks";

function TeamCard({
  id,
  name,
  slug,
  aggregates,
  form
}: {
  id: number;
  name: string;
  slug: string;
  aggregates: { goals_per_match: number; shooting_pct: number; extra_man_pct: number };
  form?: number[] | null;
}) {
  return (
    <div className="rounded-2xl border border-white bg-white/80 p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold">{name}</h3>
          <div className="mt-2 flex items-center gap-2">
            <FormDots results={form || [1, 0, -1, 1, 1]} />
            <span className="text-xs text-slate">last 5</span>
          </div>
        </div>
        <Link href={`/teams/${slug}`} className="text-xs text-wave">
          View
        </Link>
      </div>
      <div className="mt-4 grid gap-3">
        <KpiCard label="Goals/Match" value={aggregates.goals_per_match.toFixed(2)} />
        <div className="grid grid-cols-2 gap-3">
          <KpiCard label="Shooting %" value={`${(aggregates.shooting_pct * 100).toFixed(1)}%`} />
          <KpiCard label="Extra-man %" value={`${(aggregates.extra_man_pct * 100).toFixed(1)}%`} />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-3 text-xs text-slate">
        <Link href={`/compare?teamA=${id}`} className="rounded-full border border-slate/30 px-3 py-1">
          Compare
        </Link>
        <button className="rounded-full border border-slate/30 px-3 py-1">Pin</button>
      </div>
    </div>
  );
}

export default function TeamsPage() {
  const { season, stage, q, setQuery } = useFilters();
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const windowParam = params.get("window") || "5";
  const [window, setWindow] = useState(Number(windowParam));
  const [pinnedOnly, setPinnedOnly] = useState(false);
  const { data = [], isLoading } = useTeams({ season, stage, q });

  function updateWindow(value: number) {
    setWindow(value);
    const query = new URLSearchParams(params.toString());
    query.set("window", String(value));
    router.push(`${pathname}?${query.toString()}`);
  }

  const filtered = useMemo(() => {
    if (!pinnedOnly) return data;
    return data.slice(0, 3);
  }, [data, pinnedOnly]);

  return (
    <div className="grid gap-8 lg:grid-cols-[280px_1fr]">
      <aside className="sticky top-24 h-fit rounded-2xl border border-white bg-white/80 p-5 shadow-sm">
        <h2 className="text-lg font-semibold">Filters</h2>
        <div className="mt-4 space-y-4">
          <input
            className="w-full rounded-lg border border-slate/30 px-3 py-2 text-sm"
            placeholder="Search team"
            value={q}
            onChange={(event) => setQuery(event.target.value)}
          />
          <label className="flex items-center gap-2 text-sm text-slate">
            <input type="checkbox" checked={pinnedOnly} onChange={() => setPinnedOnly(!pinnedOnly)} />
            Pinned only
          </label>
          <div className="space-y-2 text-sm text-slate">
            <p className="text-xs uppercase tracking-[0.2em]">Window</p>
            <div className="flex gap-2">
              {[5, 10, 15].map((val) => (
                <button
                  key={val}
                  onClick={() => updateWindow(val)}
                  className={`rounded-full border px-3 py-1 text-xs ${window === val ? "border-ink text-ink" : "border-slate/30"}`}
                >
                  {val}
                </button>
              ))}
            </div>
          </div>
        </div>
      </aside>

      <section className="space-y-6">
        <div className="rounded-2xl border border-white bg-white/80 p-5 shadow-sm">
          <h2 className="text-xl font-semibold">League snapshot</h2>
          <p className="text-xs text-slate">Distribution of shooting efficiency across teams.</p>
          <div className="mt-4">
            <DistributionChart
              title="Shooting% spread"
              caption="How teams convert their shots"
              categories={filtered.map((team) => team.name)}
              values={filtered.map((team) => Number((team.aggregates.shooting_pct * 100).toFixed(1)))}
            />
          </div>
        </div>

        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }).map((_, idx) => (
              <SkeletonCard key={idx} />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <EmptyStateCard
            title="No teams found"
            description="Try adjusting your filters or clear the search."
            actionLabel="Reset filters"
            actionHref="/teams"
          />
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map((team) => (
              <TeamCard
                key={team.id}
                id={team.id}
                name={team.name}
                slug={team.slug}
                aggregates={team.aggregates}
                form={team.form}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
