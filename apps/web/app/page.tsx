import Link from "next/link";

export default function HomePage() {
  return (
    <section className="grid gap-8">
      <div className="rounded-3xl border border-white bg-white/80 p-10 shadow-sm">
        <p className="text-xs uppercase tracking-[0.3em] text-slate">Champions League Analytics</p>
        <h2 className="mt-3 text-4xl font-semibold">Command center for water polo intelligence</h2>
        <p className="mt-4 max-w-2xl text-slate">
          Explore team form, matchups, and roster context with a data-first dashboard built for the Final Four.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/teams" className="rounded-full bg-wave px-5 py-2 text-sm text-white">
            Explore teams
          </Link>
          <Link href="/compare" className="rounded-full border border-slate/30 px-5 py-2 text-sm">
            Compare matchups
          </Link>
          <Link href="/matches" className="rounded-full border border-slate/30 px-5 py-2 text-sm">
            Browse matches
          </Link>
        </div>
      </div>
    </section>
  );
}
