"use client";

import dynamic from "next/dynamic";

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

export default function Sparkline({ data }: { data: number[] }) {
  const option = {
    grid: { left: 2, right: 2, top: 2, bottom: 2 },
    xAxis: { type: "category", show: false, data: data.map((_, i) => i) },
    yAxis: { type: "value", show: false },
    series: [
      {
        type: "line",
        data,
        smooth: true,
        symbol: "none",
        lineStyle: { color: "#0ea5a3", width: 2 },
        areaStyle: { color: "rgba(14,165,163,0.12)" }
      }
    ]
  };

  return <ReactECharts option={option} style={{ width: 90, height: 40 }} />;
}
