"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import type { FeatureCollection } from "geojson";
import type { PathOptions } from "leaflet";
import type { GeoEstado } from "@/types";
import { formatBRL, formatNumber } from "@/lib/formatters";

export type MapMetric = "pedidos" | "receita" | "review_score_medio";

export interface BrazilMapProps {
  data: GeoEstado[];
  metric: MapMetric;
}

/** Escala sequencial azul: branco → azul escuro (#08306B). */
function getColor(value: number, min: number, max: number): string {
  const t = max > min ? (value - min) / (max - min) : 0;
  return `rgb(${Math.round(247 - t * 239)},${Math.round(251 - t * 203)},${Math.round(255 - t * 148)})`;
}

function buildScale(data: GeoEstado[], metric: MapMetric) {
  const vals = data.map((d) => d[metric] as number);
  return { min: Math.min(...vals), max: Math.max(...vals) };
}

function buildTooltip(nome: string, sigla: string, d: GeoEstado): string {
  return `<strong>${nome} (${sigla})</strong><br/>
Pedidos: ${formatNumber(d.pedidos)}<br/>
Receita: ${formatBRL(d.receita)}<br/>
Frete médio: ${formatBRL(d.frete_medio)}<br/>
Satisfação: ${d.review_score_medio.toFixed(2)}`;
}

/**
 * Mapa choropleth do Brasil por UF usando Leaflet + GeoJSON.
 * Importado dinamicamente via BrazilMapWrapper para evitar SSR.
 */
export default function BrazilMap({ data, metric }: BrazilMapProps) {
  const [geoData, setGeoData] = useState<FeatureCollection | null>(null);

  useEffect(() => {
    fetch("/geo/brazil-states.geojson")
      .then((r) => {
        if (!r.ok) throw new Error(`GeoJSON fetch failed: ${r.status}`);
        return r.json();
      })
      .then(setGeoData)
      .catch((err) => console.error("[BrazilMap]", err));
  }, []);

  const { min, max } = buildScale(data, metric);
  const dataMap = new Map(data.map((d) => [d.estado, d]));

  if (!geoData) {
    return (
      <div
        data-testid="brazil-map-geojson-loading"
        className="h-[420px] bg-secondary animate-pulse rounded"
      />
    );
  }

  return (
    <MapContainer
      center={[-14.0, -51.0]}
      zoom={4}
      style={{ height: "420px", width: "100%" }}
      scrollWheelZoom={false}
      data-testid="brazil-map"
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      <GeoJSON
        key={metric}
        data={geoData}
        style={(feature) => {
          const sigla = feature?.properties?.sigla as string | undefined;
          const estadoData = sigla ? dataMap.get(sigla) : undefined;
          const value = estadoData ? (estadoData[metric] as number) : undefined;
          return {
            fillColor: value != null ? getColor(value, min, max) : "#E5E7EB",
            fillOpacity: 0.85,
            color: "#FFFFFF",
            weight: 1.5,
          } as PathOptions;
        }}
        onEachFeature={(feature, layer) => {
          const sigla = feature.properties?.sigla as string;
          const nome = feature.properties?.nome as string;
          const estadoData = dataMap.get(sigla);
          if (estadoData) {
            layer.bindTooltip(buildTooltip(nome, sigla, estadoData), {
              sticky: true,
            });
          }
          layer.on({
            mouseover: (e) => {
              e.target.setStyle({ weight: 3, color: "#374151" });
              e.target.bringToFront();
            },
            mouseout: (e) => {
              e.target.setStyle({ weight: 1.5, color: "#FFFFFF" });
            },
          });
        }}
      />
    </MapContainer>
  );
}
