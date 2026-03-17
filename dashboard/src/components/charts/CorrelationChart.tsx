"use client";

import { useEffect, useState } from "react";
import { loadChapterData } from "@/lib/data";
import type { GeoEstado, GeoCorrelacao } from "@/types";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Label,
} from "recharts";
import { CHART_CONFIG, CHART_COLORS, MUTED_COLOR } from "@/lib/constants";

interface ScatterPoint {
  x: number;
  y: number;
  estado: string;
}

interface TooltipPayloadItem {
  payload: ScatterPoint;
}

/**
 * Scatter plot: frete (% do valor) × review score médio por estado.
 * Exibe o resultado do teste de correlação abaixo do gráfico.
 */
export default function CorrelationChart() {
  const [points, setPoints] = useState<ScatterPoint[] | null>(null);
  const [correlacao, setCorrelacao] = useState<GeoCorrelacao | null>(null);

  useEffect(() => {
    Promise.all([
      loadChapterData<GeoEstado[]>("04_geo_estados.json"),
      loadChapterData<GeoCorrelacao>("04_geo_correlacao.json"),
    ]).then(([estados, corr]) => {
      setPoints(
        estados.map((d) => ({
          x: Math.round(d.frete_percentual * 1000) / 10,
          y: d.review_score_medio,
          estado: d.estado,
        }))
      );
      setCorrelacao(corr);
    });
  }, []);

  if (!points || !correlacao) {
    return (
      <div
        data-testid="correlation-chart-loading"
        className="h-64 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  return (
    <div data-testid="correlation-chart" className="mt-4">
      <ResponsiveContainer width="100%" height={280}>
        <ScatterChart margin={CHART_CONFIG.marginWithAxis}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="x"
            type="number"
            name="Frete %"
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
          >
            <Label
              value="Frete (% do valor do pedido)"
              offset={-10}
              position="insideBottom"
              style={{ fontSize: 11, fill: MUTED_COLOR }}
            />
          </XAxis>
          <YAxis
            dataKey="y"
            type="number"
            name="Satisfação"
            domain={[3.0, 4.3]}
            tick={{ fontSize: CHART_CONFIG.fontSizeAxis, fill: MUTED_COLOR }}
          >
            <Label
              value="Review score médio"
              angle={-90}
              position="insideLeft"
              offset={15}
              style={{ fontSize: 11, fill: MUTED_COLOR }}
            />
          </YAxis>
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            content={({ payload }) => {
              const item = payload?.[0] as TooltipPayloadItem | undefined;
              if (!item) return null;
              const p = item.payload;
              return (
                <div className="bg-white border border-border rounded p-2 text-xs font-sans shadow-sm">
                  <p className="font-semibold text-foreground">{p.estado}</p>
                  <p className="text-muted">Frete: {p.x.toFixed(1)}%</p>
                  <p className="text-muted">Score: {p.y.toFixed(2)}</p>
                </div>
              );
            }}
          />
          <Scatter data={points} fill={CHART_COLORS[0]} opacity={0.75} />
        </ScatterChart>
      </ResponsiveContainer>

      <div className="mt-3 p-3 bg-surface border border-border rounded text-xs font-sans">
        <span className="font-semibold">
          Resultado ({correlacao.teste_usado}):
        </span>{" "}
        {correlacao.significativo ? (
          <span className="text-red-600">
            Correlação negativa significativa (ρ ={" "}
            {correlacao.tamanho_efeito.toFixed(3)}, p ={" "}
            {correlacao.p_value.toFixed(4)})
          </span>
        ) : (
          <span className="text-muted">
            Sem correlação significativa (p = {correlacao.p_value.toFixed(4)})
          </span>
        )}
        {correlacao.mensagem && (
          <p className="mt-1 text-muted">{correlacao.mensagem}</p>
        )}
      </div>
    </div>
  );
}
