import type { ReactNode } from "react";

export default function StatCard({ label, value, suffix }: { label: string; value: ReactNode; suffix?: string }) {
  return (
    <div className="rounded-2xl bg-white/80 p-4 shadow-sm border border-white">
      <p className="text-xs uppercase tracking-[0.2em] text-slate">{label}</p>
      <p className="mt-2 text-2xl font-semibold">
        {value} {suffix ? <span className="text-sm text-slate">{suffix}</span> : null}
      </p>
    </div>
  );
}
