"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { RfmClustering } from "@/types";
import { CHART_COLORS, CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: number;
}

const CustomTooltip = ({ active, payload, label }: TooltipPayload) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-border rounded px-3 py-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-primary mb-1">k = {label}</p>
      <p className="text-foreground">
        Dispersão: <span className="font-medium">{payload[0].value.toLocaleString("pt-BR")}</span>
      </p>
    </div>
  );
};

/**
 * Gráfico de linha do Elbow Method (k vs inércia).
 * Indica visualmente o k ótimo com linha de referência vertical.
 */
export default function ElbowChart() {
  const [data, setData] = useState<RfmClustering | null>(null);

  useEffect(() => {
    loadChapterData<RfmClustering>("02_rfm_clustering.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="elbow-chart-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  if (!data.elbow?.length) {
    return <p className="text-muted text-sm mt-4">Sem dados disponíveis.</p>;
  }

  return (
    <div data-testid="elbow-chart" className="mt-4 h-52">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data.elbow}
          margin={{ top: 4, right: 24, bottom: 4, left: 16 }}
        >
          <CartesianGrid stroke="#E5E7EB" strokeDasharray="3 3" />
          <XAxis
            dataKey="k"
            label={{ value: "k (clusters)", position: "insideBottom", offset: -2, fontSize: 10, fill: MUTED_COLOR }}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          {data.k_otimo !== null && (
            <ReferenceLine
              x={data.k_otimo}
              stroke={CHART_COLORS[3]}
              strokeDasharray="4 2"
              label={{ value: `k=${data.k_otimo}`, position: "top", fontSize: 10, fill: CHART_COLORS[3] }}
            />
          )}
          <Line
            type="monotone"
            dataKey="inertia"
            stroke={CHART_COLORS[0]}
            strokeWidth={CHART_CONFIG.strokeWidth}
            dot={{ r: CHART_CONFIG.dotRadius, fill: CHART_COLORS[0] }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
