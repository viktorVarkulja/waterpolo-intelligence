import Link from "next/link";

export default function EmptyStateCard({
  title,
  description,
  actionLabel,
  actionHref
}: {
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-slate/40 bg-white/70 p-6 text-center">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-slate">{description}</p>
      {actionLabel && actionHref ? (
        <Link href={actionHref} className="mt-4 inline-flex rounded-full border border-slate/40 px-4 py-2 text-xs">
          {actionLabel}
        </Link>
      ) : null}
    </div>
  );
}
