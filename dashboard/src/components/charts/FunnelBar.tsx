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
  LabelList,
} from "recharts";
import { loadChapterData } from "@/lib/data";
import type { FunilConversao } from "@/types";
import { formatNumber, formatPercent } from "@/lib/formatters";
import { CHART_COLORS, CHART_CONFIG, MUTED_COLOR } from "@/lib/constants";
import { useIsMobile } from "@/lib/hooks";

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ payload: FunilConversao & { pct_base: number } }>;
}

const CustomTooltip = ({ active, payload }: TooltipPayload) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="bg-white border border-border rounded px-3 py-2 text-xs font-sans shadow-sm">
      <p className="font-semibold text-primary mb-1">{d.etapa}</p>
      <p className="text-foreground">
        Pedidos: <span className="font-medium">{formatNumber(d.pedidos)}</span>
      </p>
      {d.taxa_conversao < 1 && (
        <p className="text-foreground">
          Conversão da etapa anterior:{" "}
          <span className="font-medium">{formatPercent(d.taxa_conversao)}</span>
        </p>
      )}
    </div>
  );
};

/**
 * Barra horizontal mostrando pedidos por etapa do funil.
 * Eixo X cortado em 94% para tornar as diferenças entre etapas legíveis.
 */
export default function FunnelBar() {
  const [data, setData] = useState<Array<FunilConversao & { pct_base: number }> | null>(
    null
  );
  const isMobile = useIsMobile();

  useEffect(() => {
    loadChapterData<FunilConversao[]>("01_funil_conversao.json").then((raw) => {
      const base = raw[0]?.pedidos ?? 1;
      setData(raw.map((d) => ({ ...d, pct_base: (d.pedidos / base) * 100 })));
    });
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="funnel-bar-loading"
        className="h-52 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  if (!data.length) {
    return <p className="text-muted text-sm mt-4">Sem dados disponíveis.</p>;
  }

  return (
    <div data-testid="funnel-bar" className="mt-4">
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 4, right: isMobile ? 44 : 80, bottom: 4, left: isMobile ? 4 : 72 }}
          >
            <CartesianGrid horizontal={false} stroke="#E5E7EB" strokeDasharray="3 3" />
            <YAxis
              dataKey="etapa"
              type="category"
              tick={{ fontSize: isMobile ? 10 : CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
              width={isMobile ? 56 : 68}
              tickLine={false}
              axisLine={false}
            />
            <XAxis
              type="number"
              domain={[94, 100]}
              tickFormatter={(v: number) => `${v}%`}
              tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "#F3F4F6" }} />
            <Bar dataKey="pct_base" radius={[0, 2, 2, 0]} barSize={28}>
              {data.map((_, i) => (
                <Cell
                  key={i}
                  fill={CHART_COLORS[0]}
                  opacity={1 - i * 0.15}
                />
              ))}
              <LabelList
                dataKey="pct_base"
                position="right"
                formatter={(v: number) => `${v.toFixed(1)}%`}
                style={{ fontSize: 11, fill: "#374151", fontFamily: "sans-serif" }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-muted mt-1 italic">
        Eixo X inicia em 94% para evidenciar as diferenças entre etapas.
      </p>
    </div>
  );
}
