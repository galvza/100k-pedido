"use client";

import { useEffect, useState } from "react";
import { loadChapterData } from "@/lib/data";
import type { CohortRecompra } from "@/types";
import { formatNumber, formatPercent } from "@/lib/formatters";

interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
}

const StatCard = ({ label, value, sub }: StatCardProps) => (
  <div className="bg-white border border-border rounded p-4">
    <p className="font-sans text-xs text-muted uppercase tracking-wide mb-1">{label}</p>
    <p className="font-serif text-2xl font-bold text-primary">{value}</p>
    {sub && <p className="font-sans text-xs text-muted mt-1">{sub}</p>}
  </div>
);

/**
 * Cards resumo com as métricas gerais de recompra da base de clientes.
 */
export default function RetentionSummary() {
  const [data, setData] = useState<CohortRecompra | null>(null);

  useEffect(() => {
    loadChapterData<CohortRecompra>("03_cohort_recompra.json").then(setData);
  }, []);

  if (data === null) {
    return (
      <div
        data-testid="retention-summary-loading"
        className="h-28 bg-secondary animate-pulse rounded mt-4"
      />
    );
  }

  const diasRecompra =
    data.dias_medio_ate_recompra !== null
      ? `${data.dias_medio_ate_recompra} dias`
      : "—";

  return (
    <div
      data-testid="retention-summary"
      className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3"
    >
      <StatCard
        label="Clientes únicos"
        value={formatNumber(data.total_clientes)}
      />
      <StatCard
        label="Fizeram 2ª compra"
        value={formatNumber(data.clientes_recompra)}
        sub={`${formatPercent(data.taxa_recompra_pct / 100)} do total`}
      />
      <StatCard
        label="Taxa de recompra"
        value={formatPercent(data.taxa_recompra_pct / 100)}
        sub="sobre clientes únicos"
      />
      <StatCard
        label="Tempo até 2ª compra"
        value={diasRecompra}
        sub="média — quem voltou"
      />
    </div>
  );
}
