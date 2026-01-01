"use client";

import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export function LineChart({
  title,
  caption,
  categories,
  series
}: {
  title: string;
  caption: string;
  categories: string[];
  series: { name: string; data: number[]; color: string }[];
}) {
  const option = {
    tooltip: { trigger: "axis" },
    legend: { data: series.map((s) => s.name) },
    xAxis: { type: "category", data: categories },
    yAxis: { type: "value" },
    series: series.map((s) => ({
      name: s.name,
      type: "line",
      data: s.data,
      smooth: true,
      lineStyle: { color: s.color },
      areaStyle: { color: `${s.color}22` }
    }))
  };
  return (
    <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-sm">
      <p className="text-sm font-semibold">{title}</p>
      <p className="text-xs text-slate mb-3">{caption}</p>
      <ReactECharts option={option} style={{ height: 260 }} />
    </div>
  );
}

export function RadarChart({ title, caption, indicators, values }: { title: string; caption: string; indicators: string[]; values: number[] }) {
  const option = {
    radar: {
      indicator: indicators.map((name) => ({ name, max: 100 }))
    },
    series: [
      {
        type: "radar",
        data: [{ value: values }],
        areaStyle: { color: "rgba(14,165,163,0.2)" },
        lineStyle: { color: "#0ea5a3" }
      }
    ]
  };
  return (
    <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-sm">
      <p className="text-sm font-semibold">{title}</p>
      <p className="text-xs text-slate mb-3">{caption}</p>
      <ReactECharts option={option} style={{ height: 260 }} />
    </div>
  );
}

export function ScatterChart({ title, caption, points }: { title: string; caption: string; points: [number, number][] }) {
  const option = {
    xAxis: { type: "value" },
    yAxis: { type: "value" },
    series: [{ type: "scatter", data: points, itemStyle: { color: "#0ea5a3" } }]
  };
  return (
    <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-sm">
      <p className="text-sm font-semibold">{title}</p>
      <p className="text-xs text-slate mb-3">{caption}</p>
      <ReactECharts option={option} style={{ height: 260 }} />
    </div>
  );
}

export function DistributionChart({ title, caption, categories, values }: { title: string; caption: string; categories: string[]; values: number[] }) {
  const option = {
    xAxis: { type: "category", data: categories },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: values, itemStyle: { color: "#0ea5a3" } }]
  };
  return (
    <div className="rounded-2xl border border-white bg-white/80 p-4 shadow-sm">
      <p className="text-sm font-semibold">{title}</p>
      <p className="text-xs text-slate mb-3">{caption}</p>
      <ReactECharts option={option} style={{ height: 220 }} />
    </div>
  );
}
