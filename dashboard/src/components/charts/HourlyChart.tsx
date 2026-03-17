"use client";

import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { SazonalidadeHoraria } from "@/types";
import { formatNumber } from "@/lib/formatters";
import { CHART_CONFIG, CHART_COLORS, MUTED_COLOR } from "@/lib/constants";
import { useIsMobile } from "@/lib/hooks";

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
        {String(label).padStart(2, "0")}h
      </p>
      <p className="text-muted">Pedidos: {formatNumber(payload[0].value)}</p>
    </div>
  );
}

/**
 * Area chart de pedidos por hora do dia (0–23h).
 * Revela os picos matutino (10h) e noturno (20h).
 */
export default function HourlyChart() {
  const [data, setData] = useState<SazonalidadeHoraria[] | null>(null);
  const isMobile = useIsMobile();

  useEffect(() => {
    loadChapterData<SazonalidadeHoraria[]>(
      "05_sazonalidade_horaria.json"
    ).then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="hourly-chart-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  const avg = data.reduce((s, d) => s + d.pedidos, 0) / data.length;
  // Find the two peak hours (10h and 20h typical)
  const sorted = [...data].sort((a, b) => b.pedidos - a.pedidos);
  const peakHours = sorted.slice(0, 2).map((d) => d.hora);

  return (
    <div data-testid="hourly-chart" className="mt-4">
      <ResponsiveContainer width="100%" height={208}>
        <AreaChart
          data={data}
          margin={isMobile ? { top: 8, right: 16, bottom: 40, left: 8 } : CHART_CONFIG.marginWithAxis}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
          <XAxis
            dataKey="hora"
            tickFormatter={(h: number) => `${String(h).padStart(2, "0")}h`}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
            interval={3}
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
          {peakHours.map((h) => (
            <ReferenceLine
              key={h}
              x={h}
              stroke="#1d4ed8"
              strokeDasharray="3 3"
              label={{
                value: `${String(h).padStart(2, "0")}h`,
                position: "top",
                fill: "#1d4ed8",
                fontSize: 10,
              }}
            />
          ))}
          <Area
            type="monotone"
            dataKey="pedidos"
            stroke={CHART_COLORS[0]}
            fill={CHART_COLORS[0]}
            fillOpacity={0.22}
            strokeWidth={CHART_CONFIG.strokeWidth}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
