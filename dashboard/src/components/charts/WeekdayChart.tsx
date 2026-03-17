"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { SazonalidadeSemanal } from "@/types";
import { formatNumber } from "@/lib/formatters";
import { CHART_CONFIG, CHART_COLORS, MUTED_COLOR } from "@/lib/constants";

const LABELS: Record<number, string> = {
  1: "Seg",
  2: "Ter",
  3: "Qua",
  4: "Qui",
  5: "Sex",
  6: "Sáb",
  7: "Dom",
};

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: number;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-border rounded p-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-foreground mb-1">
        {LABELS[label ?? 1]}
      </p>
      <p className="text-muted">
        Média de pedidos: {formatNumber(Math.round(payload[0].value))}
      </p>
    </div>
  );
}

/**
 * Bar chart com pedidos médios por dia da semana (Seg–Dom).
 */
export default function WeekdayChart() {
  const [data, setData] = useState<SazonalidadeSemanal[] | null>(null);

  useEffect(() => {
    loadChapterData<SazonalidadeSemanal[]>(
      "05_sazonalidade_semanal.json"
    ).then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="weekday-chart-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  const enriched = data.map((d) => ({ ...d, label: LABELS[d.dia_semana] }));
  const maxVal = Math.max(...enriched.map((d) => d.pedidos_medio));
  const avg = enriched.reduce((s, d) => s + d.pedidos_medio, 0) / enriched.length;

  return (
    <div data-testid="weekday-chart" className="mt-4">
      <ResponsiveContainer width="100%" height={208}>
        <BarChart data={enriched} margin={CHART_CONFIG.marginWithAxis}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
          />
          <YAxis
            tickFormatter={(v: number) => formatNumber(v)}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            width={50}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={avg}
            stroke={MUTED_COLOR}
            strokeDasharray="4 4"
            label={{ value: "Média", position: "right", fill: MUTED_COLOR, fontSize: 10 }}
          />
          <Bar
            dataKey="pedidos_medio"
            radius={[CHART_CONFIG.barRadius, CHART_CONFIG.barRadius, 0, 0]}
          >
            {enriched.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.pedidos_medio === maxVal ? "#1d4ed8" : CHART_COLORS[0]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
