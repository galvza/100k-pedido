import type { Metadata } from "next";
import ChapterLayout from "@/components/layout/ChapterLayout";
import Insight from "@/components/editorial/Insight";
import Callout from "@/components/editorial/Callout";
import CohortHeatmap from "@/components/charts/CohortHeatmap";
import RetentionSummary from "@/components/charts/RetentionSummary";

export const metadata: Metadata = {
  title: "Análise de Cohort",
};

export default function CohortPage() {
  return (
    <ChapterLayout
      title="Análise de Cohort"
      subtitle="Clientes que compraram no mesmo mês retornam? Coorte a coorte, mês a mês."
      tecnicas={["CTE encadeado", "DATE_TRUNC", "DATE_DIFF", "Window Functions"]}
    >
      {/* Seção 1 — O que é */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          O que é análise de cohort?
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed">
          Uma coorte é um grupo de clientes que fez a primeira compra no mesmo
          mês. A análise acompanha cada coorte ao longo do tempo e mede a
          proporção que volta a comprar nos meses seguintes. O resultado é um
          heatmap de retenção: linhas são as coortes, colunas são os meses
          desde a primeira compra (M+0, M+1, M+2...). A célula M+0 é sempre
          100% — toda a coorte está presente no mês de estreia.
        </p>
      </section>

      {/* Seção 2 — Heatmap */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Heatmap de retenção por coorte
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Verde escuro indica alta retenção; branco indica ausência de retorno.
          Células cinzas representam períodos futuros (além do horizonte do
          dataset). O padrão triangular é esperado: coortes mais recentes têm
          menos meses de observação disponíveis.
        </p>

        <CohortHeatmap />

        <Insight>
          <strong>O padrão é consistente em todas as coortes:</strong> a
          retenção cai abruptamente de 100% (M+0) para 5–7% em M+1, depois
          para 2–4% em M+2, e se estabiliza em torno de 0,3–0,5% a partir de
          M+6. Não há coorte com recuperação significativa — o que era esperado
          para um marketplace generalista.
        </Insight>
      </section>

      {/* Seção 3 — Resumo */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Métricas gerais de recompra
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Consolidando todas as coortes, menos de 7% dos clientes únicos
          realizaram uma segunda compra em qualquer momento do dataset.
          Quem voltou levou em média 183 dias — mais de 6 meses — para fazê-lo.
        </p>

        <RetentionSummary />

        <Insight>
          <strong>93% dos clientes compraram apenas uma vez.</strong>{" "}
          Este número, que pode parecer alarmante, é na verdade o padrão do
          modelo de marketplace: o cliente compra de um vendedor via Olist,
          mas a próxima compra pode ser com outro vendedor na mesma plataforma
          — o que não aparece como recompra no nível do cliente individual.
        </Insight>
      </section>

      {/* Callout — Marketplace vs loja própria */}
      <Callout variant="info" title="Marketplace vs loja própria">
        Em e-commerces próprios, taxas de retenção de 20–40% em M+1 são
        consideradas saudáveis. Em marketplaces como Olist, Amazon ou Shopee,
        a &ldquo;retenção&rdquo; do ponto de vista do dataset reflete
        apenas recompras com o <em>mesmo vendedor</em> ou registradas com o
        mesmo <code>customer_unique_id</code>. A retenção real da
        <em> plataforma</em> é invisível neste dataset — os 93% que
        &ldquo;não voltaram&rdquo; podem ter continuado comprando via Olist,
        porém de outros vendedores.
      </Callout>
    </ChapterLayout>
  );
}
