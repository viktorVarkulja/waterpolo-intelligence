"use client";

import Link from "next/link";
import { useState } from "react";

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
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/40 bg-white/70 backdrop-blur">
      <div className="mx-auto max-w-[1280px] px-4 py-4 sm:px-6">
        <div className="flex w-full flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-start gap-3">
              <img src="/logo.svg" alt="Water Polo Intelligence" className="mt-0.5 h-12 w-12 object-contain" />
              <div>
                <p className="text-[10px] uppercase tracking-[0.3em] text-slate">Champions League</p>
                <h1 className="text-base font-semibold sm:text-lg">Water Polo Intelligence</h1>
              </div>
            </div>
            <button
              className="rounded-full border border-slate/30 px-3 py-1 text-xs text-slate md:hidden"
              onClick={() => setMobileOpen((prev) => !prev)}
              type="button"
            >
              {mobileOpen ? "Close" : "Menu"}
            </button>
          </div>

          <nav
            className={`${
              mobileOpen ? "flex" : "hidden"
            } w-full flex-col gap-3 text-sm font-medium text-slate md:flex md:w-auto md:flex-row md:items-center md:gap-5`}
          >
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 hover:text-ink"
                onClick={() => setMobileOpen(false)}
              >
                {item.label}
                {item.badge ? (
                  <span className="rounded-full border border-slate/30 px-2 py-0.5 text-[10px] uppercase">
                    {item.badge}
                  </span>
                ) : null}
              </Link>
            ))}
          </nav>

          <div className="flex w-full flex-wrap items-center gap-2 md:w-auto md:justify-end md:gap-3">
            <select
              className="w-full rounded-full border border-slate/30 bg-white px-3 py-1 text-xs sm:w-auto"
              value={season}
              onChange={(event) => setSeason(event.target.value)}
            >
              <option value="CL26">CL26</option>
              <option value="CL25">CL25</option>
            </select>
            <select
              className="w-full rounded-full border border-slate/30 bg-white px-3 py-1 text-xs sm:w-auto"
              value={stage}
              onChange={(event) => setStage(event.target.value)}
            >
              <option value="all">All stages</option>
              <option value="Group Stage">Group Stage</option>
              <option value="Final 8">Final 8</option>
              <option value="Final 4">Final 4</option>
            </select>
            <input
              className="w-full rounded-full border border-slate/30 bg-white px-3 py-1 text-xs md:w-48"
              placeholder="Search"
              value={q}
              onChange={(event) => setQuery(event.target.value)}
            />
            <FreshnessPill />
          </div>
        </div>
      </div>
    </header>
  );
}
