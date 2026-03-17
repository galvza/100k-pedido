"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { loadChapterData } from "@/lib/data";
import type { GeoEstado } from "@/types";
import type { MapMetric } from "./BrazilMap";

const METRIC_LABELS: Record<MapMetric, string> = {
  pedidos: "Pedidos",
  receita: "Receita (R$)",
  review_score_medio: "Satisfação",
};

const BrazilMapDynamic = dynamic(() => import("./BrazilMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[300px] sm:h-[420px] bg-secondary animate-pulse rounded" />
  ),
});

/**
 * Wrapper com carregamento de dados, seletor de métrica e dynamic import do mapa.
 * Separa o estado de dados do componente Leaflet (evita SSR).
 */
export default function BrazilMapWrapper() {
  const [data, setData] = useState<GeoEstado[] | null>(null);
  const [metric, setMetric] = useState<MapMetric>("pedidos");

  useEffect(() => {
    loadChapterData<GeoEstado[]>("04_geo_estados.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="brazil-map-wrapper-loading"
        className="mt-4 h-[300px] sm:h-[420px] bg-secondary animate-pulse rounded"
      />
    );
  }

  return (
    <div data-testid="brazil-map-wrapper" className="mt-4">
      <div className="flex gap-2 mb-3 flex-wrap">
        {(Object.keys(METRIC_LABELS) as MapMetric[]).map((m) => (
          <button
            key={m}
            onClick={() => setMetric(m)}
            className={`text-xs px-3 py-2.5 sm:py-1.5 min-h-[44px] sm:min-h-0 rounded border font-sans transition-colors ${
              metric === m
                ? "bg-primary text-white border-primary"
                : "bg-white text-muted border-border hover:border-primary"
            }`}
          >
            {METRIC_LABELS[m]}
          </button>
        ))}
      </div>
      <BrazilMapDynamic data={data} metric={metric} />
    </div>
  );
}
