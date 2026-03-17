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
      subtitle="De cada 100 pedidos feitos no Olist, quantos chegam de fato ao destino — e onde o processo trava?"
      tecnicas={["Subqueries encadeadas", "Lógica condicional SQL", "Cálculos de data SQL", "Agregação condicional"]}
    >
      {/* Seção 1 — Conversão por etapa */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Conversão por etapa
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          O funil abaixo acompanha cada pedido desde o momento da compra até a
          entrega final. A pergunta central é: em qual etapa o processo perde
          mais pedidos? A resposta pode surpreender — a logística do marketplace
          é mais eficiente do que a intuição sugere.
        </p>

        <FunnelBar />

        <Insight>
          <strong>De cada 100 pedidos, 97 chegam ao destino.</strong> A maior
          perda ocorre na aprovação do pagamento — 1,8% dos pedidos não passam
          dessa etapa, possivelmente por recusa de cartão ou expiração de boleto.
          A partir da aprovação, a taxa de conclusão supera 99%. Uma velocidade
          que seria impensável no varejo físico.
        </Insight>
      </section>

      {/* Seção 2 — Tempo entre etapas */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Quanto tempo leva cada etapa?
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          Se o funil mostra <em>quantos</em> pedidos avançam, o cronômetro
          mostra <em>quanto tempo</em> cada etapa consome. O gargalo não está no
          pagamento — está na estrada. A entrega é responsável por mais de 80%
          do tempo total entre a compra e o recebimento.
        </p>

        <TimelineChart />

        <Insight>
          <strong>O pagamento é aprovado em ~10 horas; a entrega leva 12 dias
          após o envio.</strong>{" "}
          O tempo total da aprovação até o recebimento é de 14,6 dias — a soma
          de 2,6 dias até o despacho e 12 dias em trânsito. A automação dos
          gateways de pagamento resolveu a velocidade financeira — o desafio
          logístico de um país continental, ainda não.
        </Insight>
      </section>

      {/* Seção 3 — Distribuição dos prazos */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Distribuição do prazo de entrega
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          A maioria das entregas se concentra entre 8 e 14 dias — o prazo padrão
          dos Correios para envios dentro do Sudeste. Mas a cauda longa revela
          outra realidade: pedidos para o Norte e Nordeste podem levar mais de
          30 dias, um reflexo da infraestrutura logística desigual do país.
        </p>

        <DeliveryHistogram />

        <Insight>
          <strong>Seis em cada dez entregas chegam em até 14 dias.</strong>{" "}
          Apenas 5,2% dos pedidos entregues levam mais de 30 dias — mas são
          justamente esses que geram as piores avaliações, como veremos no
          capítulo de Reviews.
        </Insight>
      </section>

      {/* Callout L06 */}
      <Callout variant="note" title="Limitação metodológica">
        Este funil é construído a partir do <strong>status final</strong> de
        cada pedido, não de eventos de navegação. Não capturamos abandonos de
        carrinho ou desistências antes da compra — apenas pedidos que chegaram
        a ser registrados no sistema. O funil real de conversão
        (visita → carrinho → checkout → pedido) não está disponível neste
        dataset.
      </Callout>
    </ChapterLayout>
  );
}
