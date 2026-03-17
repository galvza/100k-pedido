import type { Metadata } from "next";
import ChapterLayout from "@/components/layout/ChapterLayout";
import Insight from "@/components/editorial/Insight";
import Callout from "@/components/editorial/Callout";
import BrazilMapWrapper from "@/components/charts/BrazilMapWrapper";
import StateRanking from "@/components/charts/StateRanking";
import CorrelationChart from "@/components/charts/CorrelationChart";

export const metadata: Metadata = {
  title: "Análise Geográfica",
};

export default function GeograficoPage() {
  return (
    <ChapterLayout
      title="Análise Geográfica"
      subtitle="De onde vêm os pedidos? Como o custo do frete molda a experiência do cliente a cada quilômetro de distância?"
      tecnicas={["JOINs multi-tabela", "Teste estatístico", "Correlação estatística", "Subqueries"]}
    >
      {/* Seção 1 — Mapa interativo */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Distribuição geográfica dos pedidos
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          O mapa abaixo mostra como o e-commerce se distribui pelo Brasil. A
          concentração no Sudeste é esperada — mas o que acontece com a
          experiência do cliente à medida que o pedido viaja para longe dos
          centros logísticos? Selecione a métrica para alternar entre volume de
          pedidos, receita e satisfação.
        </p>

        <BrazilMapWrapper />

        <Insight>
          <strong>São Paulo concentra 42% dos pedidos — mas quem paga o preço da
          distância é o Norte.</strong> SP, RJ e MG respondem por ~67% do volume.
          Estados do Norte (AM, RR, AC, AP) pagam frete médio acima de R$ 50 —
          mais de 3× o custo em São Paulo — e, não por coincidência, registram
          as piores avaliações do dataset.
        </Insight>
      </section>

      {/* Seção 2 — Ranking */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Ranking dos estados
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          Reordene a tabela por qualquer métrica. O gradiente de custo entre
          regiões é visível: estados do Sudeste pagam 11–18% do valor do pedido
          em frete; estados do Norte, 42–60%. O frete como percentual do pedido
          é um indicador mais revelador do que o valor absoluto — mostra o peso
          real da logística na decisão de compra.
        </p>

        <StateRanking />
      </section>

      {/* Seção 3 — Correlação frete × satisfação */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Frete mais caro, avaliação mais baixa?
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          Cada ponto no gráfico representa um estado brasileiro. O eixo
          horizontal mostra o frete como percentual do valor do pedido; o
          vertical, o score médio de avaliação. A tendência descendente é
          clara — e o teste de correlação de Spearman confirma: existe
          associação negativa significativa (p &lt; 0,01) entre custo de frete
          e satisfação do cliente.
        </p>

        <CorrelationChart />

        <Callout variant="warning" title="Correlação não é causalidade">
          A correlação Spearman mede associação, não causalidade. O frete mais
          alto nos estados do Norte coincide com menor infraestrutura logística,
          prazos de entrega mais longos e potencial maior insatisfação com
          atrasos — fatores confundidores que o dataset não permite isolar.
          O frete pode ser um proxy da distância, que é o verdadeiro driver.
        </Callout>
      </section>
      {/* Links pro código Python */}
      <div className="mt-6 pt-4 border-t border-border">
        <p className="font-sans text-xs text-muted">
          Ver código-fonte:{" "}
          <a href="https://github.com/galvza/100k-pedidos/blob/main/pipeline/analyze/hipoteses.py" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
            pipeline/analyze/hipoteses.py
          </a>
        </p>
      </div>
    </ChapterLayout>
  );
}
