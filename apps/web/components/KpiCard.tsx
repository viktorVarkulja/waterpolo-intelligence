import type { ReactNode } from "react";

import Sparkline from "./Sparkline";

export default function KpiCard({
  label,
  value,
  delta,
  trend
}: {
  label: string;
  value: string | number;
  delta?: number | null;
  trend?: number[];
}) {
  const deltaLabel = delta === null || delta === undefined ? null : `${delta >= 0 ? "+" : ""}${delta.toFixed(2)}`;
  const deltaClass = delta === null || delta === undefined ? "text-slate" : delta >= 0 ? "text-wave" : "text-coral";
  return (
    <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-[0.2em] text-slate">{label}</p>
        {deltaLabel ? <span className={`text-xs ${deltaClass}`}>{deltaLabel}</span> : null}
      </div>
      <div className="mt-3 flex items-end justify-between">
        <p className="text-2xl font-semibold">{value}</p>
        {trend ? <Sparkline data={trend} /> : null}
      </div>
    </div>
  );
}
