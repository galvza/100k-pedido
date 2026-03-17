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
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { ReviewsDistribuicao } from "@/types";
import { formatNumber, formatPercent } from "@/lib/formatters";
import { CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";
import { useIsMobile } from "@/lib/hooks";

/** Cores semânticas por score (1=vermelho → 5=verde). */
const SCORE_COLORS: Record<number, string> = {
  1: "#DC2626",
  2: "#F97316",
  3: "#EAB308",
  4: "#84CC16",
  5: "#059669",
};

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: ReviewsDistribuicao }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-border rounded p-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-foreground">Score {d.score}</p>
      <p className="text-muted">Avaliações: {formatNumber(d.contagem)}</p>
      <p className="text-muted">Percentual: {formatPercent(d.percentual)}</p>
    </div>
  );
}

/**
 * Bar chart horizontal (layout vertical) da distribuição de scores 1–5.
 * Cores semânticas: vermelho (1) → verde (5).
 */
export default function ScoreDistribution() {
  const [data, setData] = useState<ReviewsDistribuicao[] | null>(null);
  const isMobile = useIsMobile();

  useEffect(() => {
    loadChapterData<ReviewsDistribuicao[]>(
      "06_reviews_distribuicao.json"
    ).then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="score-distribution-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  const sorted = [...data].sort((a, b) => b.score - a.score);

  return (
    <div data-testid="score-distribution" className="mt-4">
      <ResponsiveContainer width="100%" height={208}>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ ...CHART_CONFIG.margin, left: 32, right: isMobile ? 36 : 56 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" horizontal={false} />
          <XAxis
            type="number"
            tickFormatter={(v: number) => formatPercent(v / 100)}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
          />
          <YAxis
            type="category"
            dataKey="score"
            tickFormatter={(v: number) => `${v}★`}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            width={28}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="contagem"
            radius={[0, CHART_CONFIG.barRadius, CHART_CONFIG.barRadius, 0]}
            label={{
              position: "right",
              formatter: (v: number) => formatPercent(v / sorted.reduce((s, d) => s + d.contagem, 0)),
              fontSize: 10,
              fill: MUTED_COLOR,
            }}
          >
            {sorted.map((d) => (
              <Cell key={d.score} fill={SCORE_COLORS[d.score]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
