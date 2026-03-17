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
import type { ReviewsAtraso } from "@/types";
import { formatNumber } from "@/lib/formatters";
import { CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";
import { useIsMobile } from "@/lib/hooks";

function getBarColor(score: number): string {
  if (score >= 4.0) return "#059669";
  if (score >= 3.0) return "#D97706";
  return "#DC2626";
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: ReviewsAtraso }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-border rounded p-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-foreground mb-1">{d.faixa_atraso}</p>
      <p className="text-muted">Score médio: {d.score_medio.toFixed(2)}</p>
      <p className="text-muted">Pedidos: {formatNumber(d.contagem)}</p>
    </div>
  );
}

/**
 * Bar chart de score médio por faixa de atraso na entrega.
 * Evidencia a queda abrupta na satisfação conforme o atraso aumenta.
 */
export default function DelayImpact() {
  const [data, setData] = useState<ReviewsAtraso[] | null>(null);
  const isMobile = useIsMobile();

  useEffect(() => {
    loadChapterData<ReviewsAtraso[]>("06_reviews_atraso.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="delay-impact-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  return (
    <div data-testid="delay-impact" className="mt-4">
      <ResponsiveContainer width="100%" height={208}>
        <BarChart
          data={data}
          margin={isMobile ? { top: 8, right: 16, bottom: 40, left: 8 } : CHART_CONFIG.marginWithAxis}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="faixa_atraso"
            tick={{ fontSize: 10, fill: MUTED_COLOR }}
            interval={0}
            angle={-15}
            textAnchor="end"
            height={44}
          />
          <YAxis
            domain={[0, 5]}
            ticks={[1, 2, 3, 4, 5]}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            width={28}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={4.0} stroke="#374151" strokeDasharray="4 2" strokeWidth={1} />
          <Bar
            dataKey="score_medio"
            radius={[CHART_CONFIG.barRadius, CHART_CONFIG.barRadius, 0, 0]}
            label={{
              position: "top",
              formatter: (v: number) => v.toFixed(2),
              fontSize: 10,
              fill: MUTED_COLOR,
            }}
          >
            {data.map((d) => (
              <Cell key={d.faixa_atraso} fill={getBarColor(d.score_medio)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
