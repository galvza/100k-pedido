import type { Metadata } from "next";
import ChapterLayout from "@/components/layout/ChapterLayout";
import Insight from "@/components/editorial/Insight";
import Callout from "@/components/editorial/Callout";
import ScoreDistribution from "@/components/charts/ScoreDistribution";
import NpsGauge from "@/components/charts/NpsGauge";
import CategoryScores from "@/components/charts/CategoryScores";
import DelayImpact from "@/components/charts/DelayImpact";
import WordList from "@/components/charts/WordList";

export const metadata: Metadata = {
  title: "Reviews e Satisfação",
};

const GITHUB_BASE = "https://github.com/galvza/100k-pedidos/blob/main";

export default function ReviewsPage() {
  return (
    <ChapterLayout
      title="Reviews e Satisfação"
      subtitle="O que determina a nota do cliente? Spoiler: mais do que o produto em si, é a entrega que define a experiência."
      tecnicas={["Lógica condicional SQL", "Subqueries", "Teste estatístico", "NPS"]}
    >
      {/* Seção 1 — Distribuição de scores + NPS */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Distribuição de avaliações e NPS
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          A distribuição de notas no Olist segue o padrão clássico de
          marketplaces: quem tem boa experiência avalia 5; quem tem má
          experiência avalia 1. As notas intermediárias (2, 3) são
          sub-representadas — a polarização é a regra, não a exceção.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
          <div>
            <p className="font-sans text-xs text-muted uppercase tracking-wide font-semibold mb-2">
              Distribuição de scores
            </p>
            <ScoreDistribution />
          </div>
          <div>
            <p className="font-sans text-xs text-muted uppercase tracking-wide font-semibold mb-2">
              Net Promoter Score
            </p>
            <NpsGauge />
          </div>
        </div>

        <Insight>
          <strong>Com NPS de 43, o Olist ficaria na faixa média do e-commerce
          brasileiro (40–50 segundo benchmarks do setor).</strong> Scores acima
          de 50 são considerados excelentes. A distribuição em J (57% de notas
          5, 11% de notas 1) confirma a polarização: quem tem boa experiência
          vira promotor; quem tem má experiência, detrator. As notas 2 e 3
          quase não existem.
        </Insight>
      </section>

      {/* Seção 2 — Score por categoria */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Satisfação por categoria de produto
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Nem todas as categorias geram a mesma satisfação. O gráfico abaixo
          ordena do pior para o melhor score médio. A linha de referência em
          4,0 marca o limiar de &ldquo;boa satisfação&rdquo; — categorias
          abaixo dela merecem atenção do time de qualidade.
        </p>

        <CategoryScores />

        <Insight>
          <strong>Livros e instrumentos musicais têm os melhores scores;
          categorias técnicas, os piores.</strong> PC Gamer, climatização e
          tablets concentram as avaliações mais baixas — provavelmente por
          expectativas mais altas dos compradores e maior chance de defeito
          ou incompatibilidade. Produtos digitais e culturais, por outro lado,
          têm entrega simples e risco baixo de frustração.
        </Insight>
      </section>

      {/* Seção 3 — Impacto do atraso */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          Cada dia de atraso custa na avaliação
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          Mais do que preço ou qualidade do produto, a entrega no prazo é o
          principal driver de satisfação no e-commerce. O gráfico abaixo mostra
          a queda abrupta: bastam 3 dias de atraso para o score médio cair de
          4,35 para 3,89 — quase meio ponto.
        </p>

        <DelayImpact />

        <Callout variant="warning" title="Resultado do teste Mann-Whitney U">
          O teste não-paramétrico Mann-Whitney U confirma que a diferença entre
          scores de pedidos entregues no prazo vs. com atraso é estatisticamente
          significativa (p &lt; 0,001). O tamanho do efeito é grande (r = 0,48),
          reforçando que o atraso é um dos principais preditores de insatisfação.
          A mensagem para o negócio é clara: investir em logística tem retorno
          direto na satisfação.
        </Callout>
      </section>

      {/* Seção 4 — Palavras frequentes */}
      <section>
        <h2 className="font-serif text-xl font-bold text-primary mb-2">
          O que dizem as avaliações
        </h2>
        <p className="font-sans text-sm text-muted leading-relaxed mb-1">
          As palavras mais frequentes nas avaliações 5★ e 1★ revelam o que
          importa para o cliente. Um detalhe interessante: &ldquo;prazo&rdquo;
          aparece nos dois grupos — elogiado quando a entrega é rápida,
          criticado quando atrasa. A palavra que define a experiência do
          e-commerce brasileiro é a mesma: prazo.
        </p>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <WordList faixa="positiva" label="Avaliações 5★" color="text-emerald-700" />
          <WordList faixa="negativa" label="Avaliações 1★" color="text-red-700" />
        </div>
      </section>

      {/* Links pro código Python */}
      <div className="mt-6 pt-4 border-t border-border">
        <p className="font-sans text-xs text-muted">
          Ver código-fonte:{" "}
          <a href={`${GITHUB_BASE}/pipeline/analyze/predicao.py`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
            pipeline/analyze/predicao.py
          </a>
          {" · "}
          <a href={`${GITHUB_BASE}/pipeline/analyze/hipoteses.py`} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
            pipeline/analyze/hipoteses.py
          </a>
        </p>
      </div>
    </ChapterLayout>
  );
}
