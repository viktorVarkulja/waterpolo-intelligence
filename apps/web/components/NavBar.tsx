"use client";

import Link from "next/link";

import { useFilters } from "./FilterProvider";
import FreshnessPill from "./FreshnessPill";

const navItems = [
  { href: "/teams", label: "Teams" },
  { href: "/players", label: "Players" },
  { href: "/matches", label: "Matches" },
  { href: "/compare", label: "Compare" },
  { href: "/simulate", label: "Simulate", badge: "Soon" }
];

export default function NavBar() {
  const { season, stage, q, setSeason, setStage, setQuery } = useFilters();

  return (
    <header className="sticky top-0 z-50 border-b border-white/40 bg-white/70 backdrop-blur">
      <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-6 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-full bg-wave" />
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate">Champions League</p>
            <h1 className="text-lg font-semibold">Water Polo Intelligence</h1>
          </div>
        </div>

        <nav className="hidden items-center gap-5 text-sm font-medium text-slate md:flex">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="flex items-center gap-2 hover:text-ink">
              {item.label}
              {item.badge ? (
                <span className="rounded-full border border-slate/30 px-2 py-0.5 text-[10px] uppercase">
                  {item.badge}
                </span>
              ) : null}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <select
            className="rounded-full border border-slate/30 bg-white px-3 py-1 text-xs"
            value={season}
            onChange={(event) => setSeason(event.target.value)}
          >
            <option value="CL26">CL26</option>
            <option value="CL25">CL25</option>
          </select>
          <select
            className="rounded-full border border-slate/30 bg-white px-3 py-1 text-xs"
            value={stage}
            onChange={(event) => setStage(event.target.value)}
          >
            <option value="all">All stages</option>
            <option value="Group Stage">Group Stage</option>
            <option value="Final 8">Final 8</option>
            <option value="Final 4">Final 4</option>
          </select>
          <input
            className="hidden rounded-full border border-slate/30 bg-white px-3 py-1 text-xs md:block"
            placeholder="Search"
            value={q}
            onChange={(event) => setQuery(event.target.value)}
          />
          <FreshnessPill />
        </div>
      </div>
    </header>
  );
}
