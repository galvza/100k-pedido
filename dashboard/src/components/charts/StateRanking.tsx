"use client";

import { useEffect, useState } from "react";
import { loadChapterData } from "@/lib/data";
import type { GeoEstado } from "@/types";
import { formatNumber, formatBRL, formatBRLCompact, formatPercent } from "@/lib/formatters";

type SortKey = "pedidos" | "receita" | "frete_medio" | "review_score_medio";

type SortDir = "asc" | "desc";


/**
 * Tabela de ranking dos estados ordenável por pedidos, receita, frete ou score.
 */
export default function StateRanking() {
  const [data, setData] = useState<GeoEstado[] | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("pedidos");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  useEffect(() => {
    loadChapterData<GeoEstado[]>("04_geo_estados.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="state-ranking-loading"
        className="h-64 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "desc" ? "asc" : "desc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const sorted = [...data].sort((a, b) =>
    sortDir === "desc" ? b[sortKey] - a[sortKey] : a[sortKey] - b[sortKey]
  );

  const sortIndicator = (key: SortKey) =>
    sortKey === key ? (sortDir === "desc" ? " ↓" : " ↑") : "";

  const thClass = (key: SortKey | null, align: "left" | "right" = "right") =>
    `${align === "left" ? "text-left" : "text-right"} py-2 px-3 font-semibold ${
      key ? "cursor-pointer select-none hover:text-foreground" : ""
    } ${sortKey === key ? "text-primary" : "text-muted"}`;

  return (
    <div data-testid="state-ranking" className="mt-4">
      <div className="overflow-x-auto">
        <table className="w-full text-xs font-sans border-collapse">
          <thead>
            <tr className="border-b border-border">
              <th className={thClass(null, "left")}>#</th>
              <th className={thClass(null, "left")}>UF</th>
              <th className={thClass("pedidos")} onClick={() => handleSort("pedidos")}>
                Pedidos{sortIndicator("pedidos")}
              </th>
              <th className={thClass("receita")} onClick={() => handleSort("receita")}>
                Receita{sortIndicator("receita")}
              </th>
              <th className={thClass("frete_medio")} onClick={() => handleSort("frete_medio")}>
                Frete Médio{sortIndicator("frete_medio")}
              </th>
              <th className="text-right py-2 px-3 text-muted font-semibold">Frete %</th>
              <th className={thClass("review_score_medio")} onClick={() => handleSort("review_score_medio")}>
                Score{sortIndicator("review_score_medio")}
              </th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, i) => (
              <tr key={row.estado} className="border-b border-border hover:bg-surface">
                <td className="py-2 px-3 text-muted tabular-nums">{i + 1}</td>
                <td className="py-2 px-3 font-medium text-foreground">{row.estado}</td>
                <td className="py-2 px-3 text-right tabular-nums">{formatNumber(row.pedidos)}</td>
                <td className="py-2 px-3 text-right tabular-nums">{formatBRLCompact(row.receita)}</td>
                <td className="py-2 px-3 text-right tabular-nums">{formatBRL(row.frete_medio)}</td>
                <td className="py-2 px-3 text-right tabular-nums">{formatPercent(row.frete_percentual)}</td>
                <td className="py-2 px-3 text-right tabular-nums">{row.review_score_medio.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
