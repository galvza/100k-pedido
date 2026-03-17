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
  Cell,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { RfmSegmento } from "@/types";
import { formatNumber, formatPercent, formatBRL } from "@/lib/formatters";
import { CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";

/** Cor semântica por segmento RFM. */
const SEGMENT_COLORS: Record<string, string> = {
  "Campeões":  "#2563EB",
  "Fiéis":     "#059669",
  "Potenciais": "#0891B2",
  "Em Risco":  "#D97706",
  "Perdidos":  "#DC2626",
};

const DEFAULT_COLOR = "#6B7280";

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ payload: RfmSegmento }>;
}

const CustomTooltip = ({ active, payload }: TooltipPayload) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-border rounded px-3 py-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-primary mb-1">{d.segmento}</p>
      <p className="text-foreground">
        Clientes: <span className="font-medium">{formatNumber(d.contagem)}</span>
        {" "}(<span className="font-medium">{formatPercent(d.percentual / 100)}</span>)
      </p>
      <p className="text-foreground">
        Recência média: <span className="font-medium">{d.recencia_media} dias</span>
      </p>
      <p className="text-foreground">
        Gasto médio: <span className="font-medium">{formatBRL(d.monetario_medio)}</span>
      </p>
    </div>
  );
};

/**
 * Barras horizontais dos segmentos RFM com cores semânticas por grupo.
 */
export default function RfmSegmentChart() {
  const [data, setData] = useState<RfmSegmento[] | null>(null);

  useEffect(() => {
    loadChapterData<RfmSegmento[]>("02_rfm_segmentos.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="rfm-segment-chart-loading"
        className="h-56 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  if (!data.length) {
    return <p className="text-muted text-sm mt-4">Sem dados disponíveis.</p>;
  }

  const sorted = [...data].sort((a, b) => b.contagem - a.contagem);

  return (
    <div data-testid="rfm-segment-chart" className="mt-4 h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 4, right: 80, bottom: 4, left: 72 }}
        >
          <CartesianGrid horizontal={false} stroke="#E5E7EB" strokeDasharray="3 3" />
          <YAxis
            dataKey="segmento"
            type="category"
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            width={68}
            tickLine={false}
            axisLine={false}
          />
          <XAxis
            type="number"
            tickFormatter={(v: number) => formatNumber(v)}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "#F3F4F6" }} />
          <Bar dataKey="contagem" radius={[0, 2, 2, 0]} barSize={28}>
            {sorted.map((entry) => (
              <Cell
                key={entry.segmento}
                fill={SEGMENT_COLORS[entry.segmento] ?? DEFAULT_COLOR}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
