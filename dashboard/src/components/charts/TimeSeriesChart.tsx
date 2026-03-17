"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { SazonalidadeMensal } from "@/types";
import { formatBRLCompact, formatNumber } from "@/lib/formatters";
import { CHART_CONFIG, CHART_COLORS, MUTED_COLOR } from "@/lib/constants";
import { useIsMobile } from "@/lib/hooks";
import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";

function tickMonth(iso: string): string {
  try {
    const d = parseISO(`${iso}-01`);
    const s = format(d, "MMM/yy", { locale: ptBR });
    return s.charAt(0).toUpperCase() + s.slice(1);
  } catch {
    return iso;
  }
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string }>;
  label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-border rounded p-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-foreground mb-1">{label ? tickMonth(label) : ""}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {p.name === "Receita" ? formatBRLCompact(p.value) : p.name === "Média móvel" ? formatBRLCompact(p.value) : formatNumber(p.value)}
        </p>
      ))}
    </div>
  );
}

/**
 * Série temporal mensal de receita com média móvel 3m.
 * Duas linhas: receita mensal (azul) + MA 3m (verde tracejada).
 */
export default function TimeSeriesChart() {
  const [data, setData] = useState<SazonalidadeMensal[] | null>(null);
  const isMobile = useIsMobile();

  useEffect(() => {
    loadChapterData<SazonalidadeMensal[]>("05_sazonalidade_mensal.json").then(
      setData
    );
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="time-series-loading"
        className="h-72 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  if (!data.length) {
    return <p className="text-muted text-sm mt-4">Sem dados disponíveis.</p>;
  }

  return (
    <div data-testid="time-series-chart" className="mt-4">
      <ResponsiveContainer width="100%" height={isMobile ? 240 : 288}>
        <LineChart data={data} margin={{ ...CHART_CONFIG.marginWithAxis, left: isMobile ? 40 : 56 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="mes"
            tickFormatter={tickMonth}
            tick={{ fontSize: isMobile ? 9 : CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            interval={isMobile ? 4 : 2}
          />
          <YAxis
            tickFormatter={(v: number) => formatBRLCompact(v)}
            tick={{ fontSize: isMobile ? 9 : CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            width={isMobile ? 48 : 64}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            x="2017-11"
            stroke="#ef4444"
            strokeDasharray="4 4"
            label={{
              value: isMobile ? "BF '17" : "Black Friday '17",
              position: "top",
              fill: "#ef4444",
              fontSize: isMobile ? 9 : 12,
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="receita"
            name="Receita"
            stroke={CHART_COLORS[0]}
            strokeWidth={CHART_CONFIG.strokeWidth}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="media_movel_3m"
            name="Média móvel"
            stroke={CHART_COLORS[1]}
            strokeWidth={CHART_CONFIG.strokeWidth}
            strokeDasharray="6 3"
            dot={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
