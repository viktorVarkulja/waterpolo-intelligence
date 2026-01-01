"use client";

import { createContext, useContext, useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

type Filters = {
  season: string;
  stage: string;
  q: string;
  setSeason: (value: string) => void;
  setStage: (value: string) => void;
  setQuery: (value: string) => void;
};

const FilterContext = createContext<Filters | null>(null);

function useQueryParamUpdater() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  return (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname);
  };
}

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const searchParams = useSearchParams();
  const updateParam = useQueryParamUpdater();

  const season = searchParams.get("season") || "CL26";
  const stage = searchParams.get("stage") || "all";
  const q = searchParams.get("q") || "";

  const value = useMemo(
    () => ({
      season,
      stage,
      q,
      setSeason: (val: string) => updateParam("season", val),
      setStage: (val: string) => updateParam("stage", val),
      setQuery: (val: string) => updateParam("q", val)
    }),
    [season, stage, q, updateParam]
  );

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

export function useFilters() {
  const ctx = useContext(FilterContext);
  if (!ctx) {
    throw new Error("useFilters must be used within FilterProvider");
  }
  return ctx;
}
