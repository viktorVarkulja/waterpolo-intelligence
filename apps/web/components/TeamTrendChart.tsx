"use client";

import dynamic from "next/dynamic";
import type { TrendPoint } from "../lib/api";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export default function TeamTrendChart({ points }: { points: TrendPoint[] }) {
  const option = {
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: points.map((p) => `M${p.match_index}`),
      axisLine: { lineStyle: { color: "#94a3b8" } }
    },
    yAxis: {
      type: "value",
      axisLine: { lineStyle: { color: "#94a3b8" } }
    },
    series: [
      {
        name: "Shooting %",
        type: "line",
        data: points.map((p) => Number((p.shooting_pct * 100).toFixed(1))),
        smooth: true,
        lineStyle: { color: "#0ea5a3" },
        areaStyle: { color: "rgba(14,165,163,0.12)" }
      }
    ]
  };

  return (
    <div className="rounded-2xl bg-white/80 p-4 border border-white shadow-sm">
      <p className="text-sm font-semibold">Rolling shooting efficiency</p>
      <ReactECharts option={option} style={{ height: 260 }} />
    </div>
  );
}
