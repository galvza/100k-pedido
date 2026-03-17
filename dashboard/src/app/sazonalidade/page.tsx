import type { Metadata } from "next";
import ChapterLayout from "@/components/layout/ChapterLayout";
import Insight from "@/components/editorial/Insight";
import Callout from "@/components/editorial/Callout";
import TimeSeriesChart from "@/components/charts/TimeSeriesChart";
import WeekdayChart from "@/components/charts/WeekdayChart";
import HourlyChart from "@/components/charts/HourlyChart";

export const metadata: Metadata = {
  title: "Sazonalidade",
};

export default function SazonalidadePage() {
  return (
    <ChapterLayout
      title="Sazonalidade"
      subtitle="Quando os brasileiros compram online? Tendência de crescimento, Black Friday, dia da semana e hora do dia revelam padrões previsíveis — e oportunidades."
      tecnicas={["Cálculos de data SQL", "Extração temporal SQL", "Funções analíticas SQL", "Comparação entre períodos", "Média Móvel"]}
    >
      {/* Seção 1 — Série temporal mensal */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Tendência de receita mensal
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          O dataset cobre 20 meses (jan/2017–ago/2018) de um marketplace em
          fase de crescimento acelerado. A linha tracejada é a média móvel de
          3 meses, que suaviza ruídos pontuais e torna a tendência mais
          legível. Um mês se destaca claramente: novembro de 2017.
        </p>

        <TimeSeriesChart />

        <Insight>
          <strong>A receita cresceu 8× em 20 meses — de R$ 110 mil para
          ~R$ 890 mil.</strong> O pico de novembro/2017 (Black Friday) trouxe
          receita ~67% acima do mês anterior, mas foi temporário: o período
          pós-BF teve queda natural. A média móvel mostra que a tendência de
          longo prazo retomou o crescimento em 2018, indicando que o Olist
          estava em expansão sustentada, não apenas inflado por promoções.
        </Insight>
      </section>

      {/* Seção 2 — Padrão semanal */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Pedidos por dia da semana
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          Quando o brasileiro compra online durante a semana? O padrão é claro
          e consistente ao longo de todo o período: mais pedidos no início da
          semana, queda progressiva até o domingo. Por que segundas-feiras
          lideram?
        </p>

        <WeekdayChart />

        <Insight>
          <strong>Segunda-feira tem ~88% mais pedidos que domingo.</strong>{" "}
          O consumidor pesquisa no fim de semana mas finaliza a compra no
          início da semana — possivelmente no horário de trabalho, quando tem
          acesso ao computador. Sábado e domingo concentram menos de 20% do
          volume semanal. Para campanhas de marketing, segunda e terça são os
          dias de maior conversão potencial.
        </Insight>
      </section>

      {/* Seção 3 — Padrão horário */}
      <section>
        <h2 className="font-serif text-xl sm:text-2xl font-bold text-primary mb-2">
          Pedidos por hora do dia
        </h2>
        <p className="font-sans text-base text-muted leading-relaxed mb-1">
          O e-commerce brasileiro tem dois horários nobres. A curva abaixo
          mostra a distribuição dos pedidos ao longo das 24 horas — e revela
          que o consumo online tem ritmo próprio, diferente do varejo físico.
        </p>

        <HourlyChart />

        <Insight>
          <strong>Dois picos: 10h (horário de trabalho) e 20h (após o
          jantar).</strong> O pico noturno supera ligeiramente o matutino,
          sugerindo que parte dos consumidores navega após o expediente. O
          vale entre 3h e 5h é o mínimo absoluto (67 pedidos). Para e-mail
          marketing e notificações push, as janelas de 9–11h e 19–21h
          oferecem a maior probabilidade de conversão.
        </Insight>

        <Callout variant="note" title="Fuso horário">
          Todos os horários estão em UTC-3 (horário de Brasília). O dataset
          não discrimina fusos dos estados do Norte (AM, AC, RR — UTC-4 e
          UTC-5), então os horários para esses estados podem ter um desvio
          de 1–2 horas.
        </Callout>
      </section>
      {/* Links pro código Python */}
      <div className="mt-6 pt-4 border-t border-border">
        <p className="font-sans text-xs text-muted">
          Ver código-fonte:{" "}
          <a href="https://github.com/galvza/100k-pedidos/blob/main/notebooks/02_analise_estatistica.ipynb" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
            notebooks/02_analise_estatistica.ipynb
          </a>
        </p>
      </div>
    </ChapterLayout>
  );
}
