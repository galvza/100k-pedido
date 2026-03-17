"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { ReviewsCategorias } from "@/types";
import { formatNumber } from "@/lib/formatters";
import { CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";
import { useIsMobile } from "@/lib/hooks";

/** Score baixo (< 3.5) → vermelho, médio → âmbar, alto (>= 4.0) → verde. */
function getScoreColor(score: number): string {
  if (score >= 4.0) return "#059669";
  if (score >= 3.5) return "#D97706";
  return "#DC2626";
}

function formatCategoria(cat: string): string {
  return cat.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: ReviewsCategorias }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-border rounded p-2 text-xs font-sans shadow-sm max-w-52">
      <p className="font-semibold text-foreground mb-1">
        {formatCategoria(d.categoria)}
      </p>
      <p className="text-muted">Score médio: {d.score_medio.toFixed(2)}</p>
      <p className="text-muted">Reviews: {formatNumber(d.total_reviews)}</p>
    </div>
  );
}

/**
 * Bar chart horizontal de score médio por categoria de produto.
 * Ordenado do menor para o maior score. Linha de referência em 4,0.
 */
export default function CategoryScores() {
  const [data, setData] = useState<ReviewsCategorias[] | null>(null);
  const isMobile = useIsMobile();

  useEffect(() => {
    loadChapterData<ReviewsCategorias[]>(
      "06_reviews_categorias.json"
    ).then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="category-scores-loading"
        className="h-96 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  // Ordenar do menor para o maior score (pior no topo)
  const sorted = [...data].sort((a, b) => a.score_medio - b.score_medio);
  const height = Math.max(320, sorted.length * 24 + 64);

  return (
    <div data-testid="category-scores" className="mt-4">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 8, right: isMobile ? 32 : 48, bottom: 8, left: isMobile ? 8 : 160 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
          <XAxis
            type="number"
            domain={[1, 5]}
            tickCount={isMobile ? 3 : 5}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
          />
          <YAxis
            type="category"
            dataKey="categoria"
            tickFormatter={formatCategoria}
            tick={{ fontSize: isMobile ? 9 : 10, fill: MUTED_COLOR }}
            width={isMobile ? 88 : 152}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine x={4.0} stroke="#374151" strokeDasharray="4 2" strokeWidth={1} />
          <Bar
            dataKey="score_medio"
            radius={[0, CHART_CONFIG.barRadius, CHART_CONFIG.barRadius, 0]}
            label={{
              position: "right",
              formatter: (v: number) => v.toFixed(2),
              fontSize: 10,
              fill: MUTED_COLOR,
            }}
          >
            {sorted.map((d) => (
              <Cell key={d.categoria} fill={getScoreColor(d.score_medio)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
