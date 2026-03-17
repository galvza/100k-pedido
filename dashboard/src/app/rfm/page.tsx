import type { Metadata } from "next";
import ChapterLayout from "@/components/layout/ChapterLayout";
import Insight from "@/components/editorial/Insight";
import Callout from "@/components/editorial/Callout";
import RfmSegmentChart from "@/components/charts/RfmSegmentChart";
import RfmDistribution from "@/components/charts/RfmDistribution";
import ElbowChart from "@/components/charts/ElbowChart";
import ClusterScatter from "@/components/charts/ClusterScatter";

export const metadata: Metadata = {
  title: "Segmentação RFM",
};

export default function RfmPage() {
  return (
    <ChapterLayout
      title="Segmentação RFM"
      subtitle="Quem são os clientes mais valiosos — e quais estão prestes a desaparecer?"
      tecnicas={["Ranking por quartis", "Funções analíticas SQL", "Clustering K-Means", "Normalização de dados", "Validação de clusters"]}
    >
      {/* Seção 1 — O que é RFM? */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          O que é RFM?
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          RFM é um modelo clássico de segmentação que classifica clientes por
          comportamento de compra em três dimensões: <strong>Recência</strong>{" "}
          (há quantos dias fez a última compra),{" "}
          <strong>Frequência</strong> (quantas vezes comprou)
          e <strong>Valor Monetário</strong> (quanto gastou no total). Cada
          dimensão recebe uma nota de 1 a 5, gerando um score combinado que
          posiciona o cliente em um dos segmentos abaixo.
        </p>

        <RfmSegmentChart />

        <Insight>
          <strong>Um em cada três clientes nunca mais voltou.</strong>{" "}
          O segmento &ldquo;Perdidos&rdquo; concentra 34% da base — compraram
          há mais de 480 dias e não retornaram. No extremo oposto, os
          Campeões (8,5%) gastam em média R$ 612 por cliente — quase 7× mais
          do que os Perdidos (R$ 92). O desafio do marketplace é transformar
          compradores ocasionais em recorrentes.
        </Insight>
      </section>

      {/* Seção 2 — Distribuição das métricas */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Distribuição das métricas
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Os histogramas revelam o perfil real da base. A distribuição de
          frequência é o dado mais revelador: a concentração massiva em
          &ldquo;1 compra&rdquo; não é um bug — é a realidade estrutural de
          um marketplace onde a lealdade é ao produto, não à plataforma.
        </p>

        <RfmDistribution />

        <Insight>
          <strong>93,3% dos clientes compraram apenas uma vez.</strong> Num
          marketplace, isso é esperado: o cliente encontra um produto, compra e
          raramente retorna pela plataforma. A frequência média de 1,07 pedidos
          confirma que Recência e Valor Monetário são as dimensões mais úteis
          para segmentação neste contexto. A análise de cohort (capítulo 3)
          aprofunda essa dinâmica.
        </Insight>
      </section>

      {/* Seção 3 — Segmentação automática */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Quantos perfis de cliente existem?
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Pedimos ao algoritmo que encontrasse grupos naturais entre os clientes,
          baseado no comportamento de compra. O gráfico abaixo mostra que a
          partir de 4 grupos, adicionar mais não melhora significativamente a
          separação — por isso escolhemos 4 perfis.
        </p>

        <ElbowChart />

        <p className="font-sans text-sm text-muted leading-relaxed mt-4 mb-1">
          Cada bolha representa um perfil de cliente encontrado pelo algoritmo.
          Quanto mais à esquerda, mais recente a última compra. Quanto mais
          acima, maior o gasto médio. O tamanho indica quantos clientes estão
          naquele perfil.
        </p>

        <ClusterScatter />

        <Insight>
          O Cluster A (VIP) concentra clientes com recência muito baixa e gasto
          alto — equivale naturalmente ao segmento &ldquo;Campeões&rdquo; da
          abordagem manual. O Cluster D (Perdidos) alinha-se com o segmento
          homônimo: alta recência (distantes no tempo) e baixo valor. A
          segmentação automática corrobora a manual, com a vantagem de não
          exigir definição prévia de limites.
        </Insight>
      </section>

      {/* Seção 4 — Manual vs Automático */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Manual vs Automático — qual usar?
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed">
          As duas abordagens são complementares. A segmentação manual (por
          quartis) é interpretável e diretamente acionável: cada segmento tem
          nome, critério claro e estratégia de marketing associada. Já o
          K-Means descobre estruturas sem pressupostos — útil para validar se
          os segmentos manuais fazem sentido nos dados ou para revelar subgrupos
          não óbvios.
        </p>

        <Callout variant="info" title="Convergência dos métodos">
          O Silhouette Score médio de 0,35 para k = 4 indica uma separação
          moderada — esperada dado que 93% dos clientes têm frequência 1,
          colapsando dimensionalidade. Mesmo assim, os 4 clusters do K-Means
          correspondem qualitativamente aos 5 segmentos manuais, validando a
          lógica de segmentação escolhida.
        </Callout>
      </section>
    </ChapterLayout>
  );
}
