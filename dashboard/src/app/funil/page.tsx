import type { Metadata } from "next";
import ChapterLayout from "@/components/layout/ChapterLayout";
import Insight from "@/components/editorial/Insight";
import Callout from "@/components/editorial/Callout";
import FunnelBar from "@/components/charts/FunnelBar";
import TimelineChart from "@/components/charts/TimelineChart";
import DeliveryHistogram from "@/components/charts/DeliveryHistogram";

export const metadata: Metadata = {
  title: "Funil de Vendas",
};

export default function FunilPage() {
  return (
    <ChapterLayout
      title="Funil de Vendas"
      subtitle="Quantos pedidos completam cada etapa — da compra à entrega no cliente?"
      tecnicas={["CTEs", "CASE WHEN", "DATE_DIFF", "Agregação condicional"]}
    >
      {/* Seção 1 — Conversão por etapa */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Conversão por etapa
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          O funil mede a proporção de pedidos que avançam em cada estágio do
          processo: compra, aprovação do pagamento, envio à transportadora e
          entrega ao cliente. Cada barra representa o percentual em relação ao
          total de pedidos realizados.
        </p>

        <FunnelBar />

        <Insight>
          <strong>97,0% dos pedidos chegam ao destino.</strong> A maior perda
          ocorre na aprovação do pagamento — 1,8% dos pedidos não passam dessa
          etapa, possivelmente por recusa de cartão ou expiração de boleto.
          Do pagamento aprovado em diante, a taxa de conclusão é acima de 99%.
        </Insight>
      </section>

      {/* Seção 2 — Tempo entre etapas */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Quanto tempo leva cada etapa?
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Cada barra representa o tempo médio decorrido entre a etapa e a
          anterior. O pagamento é aprovado em menos de 12 horas; o envio à
          transportadora leva em média 2,5 dias; e a entrega final domina o
          tempo total com mais de 12 dias.
        </p>

        <TimelineChart />

        <Insight>
          <strong>O prazo de entrega responde por 80% do tempo total.</strong>{" "}
          Da aprovação até o cliente receber, passam em média 14,6 dias. A
          etapa mais rápida é a aprovação do pagamento (&lt; 0,5 dia),
          refletindo a automação dos gateways de pagamento.
        </Insight>
      </section>

      {/* Seção 3 — Distribuição dos prazos */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Distribuição do prazo de entrega
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          A distribuição mostra a concentração de entregas por faixa de prazo.
          A curva é assimétrica à direita: a maioria das entregas se concentra
          entre 8 e 14 dias, com uma cauda longa de pedidos que demoram mais
          de 30 dias — geralmente destinados a regiões remotas do Norte e
          Nordeste.
        </p>

        <DeliveryHistogram />

        <Insight>
          <strong>62% das entregas acontecem em até 14 dias.</strong> Apenas
          5,2% dos pedidos entregues levam mais de 30 dias. O pico na faixa de
          8–14 dias reflete o prazo padrão dos Correios para envios dentro dos
          estados mais populosos do Sudeste.
        </Insight>
      </section>

      {/* Callout L06 */}
      <Callout variant="note" title="Limitação metodológica (L06)">
        Este funil é construído a partir do <strong>status final</strong> de
        cada pedido, não de eventos de navegação. Isso significa que não
        capturamos abandonos de carrinho ou desistências antes da compra —
        apenas pedidos que chegaram a ser registrados no sistema Olist. O
        funil real de conversão (visita → carrinho → checkout → pedido) não
        está disponível neste dataset.
      </Callout>
    </ChapterLayout>
  );
}
