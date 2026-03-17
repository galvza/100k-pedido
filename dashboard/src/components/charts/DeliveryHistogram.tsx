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
import type { FunilTempos } from "@/types";
import { formatNumber } from "@/lib/formatters";
import { CHART_COLORS, CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ value: number; payload: FunilTempos }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: TooltipPayload) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-border rounded px-3 py-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-primary mb-1">{label}</p>
      <p className="text-foreground">
        Entregas: <span className="font-medium">{formatNumber(d.contagem)}</span>
      </p>
      <p className="text-foreground">
        Média: <span className="font-medium">{d.media_dias_na_faixa.toFixed(1)} dias</span>
      </p>
    </div>
  );
};

/**
 * Histograma de faixas de tempo de entrega.
 */
export default function DeliveryHistogram() {
  const [data, setData] = useState<FunilTempos[] | null>(null);

  useEffect(() => {
    loadChapterData<FunilTempos[]>("01_funil_tempos.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="delivery-histogram-loading"
        className="h-56 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  if (!data.length) {
    return <p className="text-muted text-sm mt-4">Sem dados disponíveis.</p>;
  }

  return (
    <div data-testid="delivery-histogram" className="mt-4 h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 4, right: 16, bottom: 4, left: 16 }}
        >
          <CartesianGrid vertical={false} stroke="#E5E7EB" strokeDasharray="3 3" />
          <XAxis
            dataKey="faixa"
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tickFormatter={(v: number) => formatNumber(v)}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
            width={48}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#F3F4F6" }} />
          <Bar
            dataKey="contagem"
            fill={CHART_COLORS[2]}
            radius={[2, 2, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
