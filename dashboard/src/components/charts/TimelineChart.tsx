"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { FunilConversao } from "@/types";
import { CHART_COLORS, CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ value: number; payload: FunilConversao }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: TooltipPayload) => {
  if (!active || !payload?.length) return null;
  const dias = payload[0].value;
  return (
    <div className="bg-white border border-border rounded px-3 py-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-primary mb-1">{label}</p>
      <p className="text-foreground">
        Tempo médio:{" "}
        <span className="font-medium">
          {dias === 0 ? "referência" : `${dias.toFixed(2)} dias`}
        </span>
      </p>
    </div>
  );
};

/**
 * Gráfico de barras mostrando tempo médio entre etapas do funil.
 */
export default function TimelineChart() {
  const [data, setData] = useState<FunilConversao[] | null>(null);

  useEffect(() => {
    loadChapterData<FunilConversao[]>("01_funil_conversao.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="timeline-chart-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  if (!data.length) {
    return <p className="text-muted text-sm mt-4">Sem dados disponíveis.</p>;
  }

  return (
    <div data-testid="timeline-chart" className="mt-4 h-52">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
        >
          <CartesianGrid vertical={false} stroke="#E5E7EB" strokeDasharray="3 3" />
          <XAxis
            dataKey="etapa"
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={(v: number) => `${v}d`}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
            width={30}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#F3F4F6" }} />
          <Bar
            dataKey="tempo_medio_dias"
            fill={CHART_COLORS[1]}
            radius={[2, 2, 0, 0]}
            barSize={36}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
