"use client";

import { useEffect, useState } from "react";
import { loadChapterData } from "@/lib/data";
import type { ReviewsDistribuicao } from "@/types";
import { formatPercent } from "@/lib/formatters";

function getNpsLabel(nps: number): { label: string; color: string } {
  if (nps > 50) return { label: "Excelente", color: "text-emerald-600" };
  if (nps > 25) return { label: "Bom", color: "text-green-600" };
  if (nps > 0) return { label: "Regular", color: "text-amber-600" };
  return { label: "Crítico", color: "text-red-600" };
}

/**
 * Indicador visual do NPS calculado a partir da distribuição de scores.
 * Promotores = score 5; Detratores = scores 1-2; Neutros = scores 3-4.
 * NPS = (% promotores - % detratores) × 100.
 */
export default function NpsGauge() {
  const [data, setData] = useState<ReviewsDistribuicao[] | null>(null);

  useEffect(() => {
    loadChapterData<ReviewsDistribuicao[]>(
      "06_reviews_distribuicao.json"
    ).then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="nps-gauge-loading"
        className="h-28 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  const promotores = data.find((d) => d.score === 5)?.percentual ?? 0;
  const detratores =
    (data.find((d) => d.score === 1)?.percentual ?? 0) +
    (data.find((d) => d.score === 2)?.percentual ?? 0);
  const neutros =
    (data.find((d) => d.score === 3)?.percentual ?? 0) +
    (data.find((d) => d.score === 4)?.percentual ?? 0);
  const nps = Math.round((promotores - detratores) * 100);
  const { label, color } = getNpsLabel(nps);

  return (
    <div
      data-testid="nps-gauge"
      className="mt-4 flex flex-col sm:flex-row gap-4 items-start sm:items-center"
    >
      {/* Score central */}
      <div className="bg-white border border-border rounded p-6 flex flex-col items-center min-w-[120px]">
        <p className="font-sans text-xs text-muted uppercase tracking-wide mb-1">NPS</p>
        <p
          data-testid="nps-value"
          className={`font-serif text-4xl font-bold ${color}`}
        >
          {nps}
        </p>
        <span className={`font-sans text-xs font-semibold mt-1 ${color}`}>
          {label}
        </span>
      </div>

      {/* Breakdown */}
      <div className="flex-1 w-full grid grid-cols-3 gap-2 sm:gap-3">
        <div className="bg-white border border-border rounded p-2 sm:p-3 text-center">
          <p className="font-sans text-[10px] sm:text-xs text-muted uppercase tracking-wide mb-1">Promotores</p>
          <p className="font-serif text-lg sm:text-xl font-bold text-emerald-600">
            {formatPercent(promotores)}
          </p>
          <p className="font-sans text-[10px] sm:text-xs text-muted">score 5★</p>
        </div>
        <div className="bg-white border border-border rounded p-2 sm:p-3 text-center">
          <p className="font-sans text-[10px] sm:text-xs text-muted uppercase tracking-wide mb-1">Neutros</p>
          <p className="font-serif text-lg sm:text-xl font-bold text-amber-600">
            {formatPercent(neutros)}
          </p>
          <p className="font-sans text-[10px] sm:text-xs text-muted">score 3–4★</p>
        </div>
        <div className="bg-white border border-border rounded p-2 sm:p-3 text-center">
          <p className="font-sans text-[10px] sm:text-xs text-muted uppercase tracking-wide mb-1">Detratores</p>
          <p className="font-serif text-lg sm:text-xl font-bold text-red-600">
            {formatPercent(detratores)}
          </p>
          <p className="font-sans text-[10px] sm:text-xs text-muted">score 1–2★</p>
        </div>
      </div>
    </div>
  );
}
