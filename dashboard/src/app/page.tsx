import Link from "next/link";
import TechBadge from "@/components/editorial/TechBadge";
import { CHAPTER_ORDER, CHAPTER_TITLES } from "@/lib/constants";

const CHAPTER_META: Record<
  string,
  { num: string; description: string; tecnicas: string[] }
> = {
  funil: {
    num: "01",
    description:
      "De cada 100 pedidos, quantos chegam ao destino? O gargalo não está onde você imagina.",
    tecnicas: ["JOINs", "Subqueries encadeadas", "Funil de conversão"],
  },
  rfm: {
    num: "02",
    description:
      "Um em cada três clientes nunca mais voltou. Quem são os valiosos — e os que já se foram?",
    tecnicas: ["Funções analíticas SQL", "Clustering K-Means"],
  },
  cohort: {
    num: "03",
    description:
      "A taxa de recompra de 3% parece baixa — mas conta uma história conhecida do marketplace.",
    tecnicas: ["Subqueries encadeadas", "Pivot", "Retenção"],
  },
  geografico: {
    num: "04",
    description:
      "SP concentra 42% dos pedidos. O Norte paga 3× mais frete — e avalia pior. Coincidência?",
    tecnicas: ["GROUP BY", "Correlação estatística", "Geoespacial"],
  },
  sazonalidade: {
    num: "05",
    description:
      "Black Friday, segundas-feiras e o horário nobre do e-commerce: quando o Brasil compra online.",
    tecnicas: ["Cálculos de data SQL", "Decomposição sazonal", "Série temporal"],
  },
  reviews: {
    num: "06",
    description:
      "Cada dia de atraso custa meio ponto na avaliação. O frete define a experiência mais do que o produto.",
    tecnicas: ["Análise de texto", "Teste estatístico"],
  },
};

const STATS = [
  { value: "99.441", label: "pedidos analisados" },
  { value: "9", label: "tabelas relacionais" },
  { value: "6", label: "capítulos analíticos" },
  { value: "2016–2018", label: "período coberto" },
];

const SKILLS = [
  {
    area: "SQL",
    items: ["DuckDB", "JOINs complexos", "Subqueries encadeadas", "Funções analíticas", "Agregações"],
  },
  {
    area: "Python",
    items: ["pandas", "scipy", "scikit-learn", "statsmodels", "pytest"],
  },
  {
    area: "Frontend",
    items: ["Next.js 14", "TypeScript", "Recharts", "Tailwind CSS", "Vitest"],
  },
];

export default function Home() {
  return (
    <main>
      {/* Hero */}
      <section className="bg-surface border-b border-border">
        <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <p className="font-sans text-sm font-medium text-accent uppercase tracking-widest mb-4">
            Projeto de portfólio — Análise de dados
          </p>
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-bold text-primary text-balance leading-tight">
            100 mil pedidos.
            <br />
            O que eles revelam?
          </h1>
          <p className="font-serif text-xl sm:text-2xl text-muted mt-3 text-balance">
            Raio-X do E-commerce Brasileiro
          </p>
          <p className="font-sans text-base text-muted mt-6 max-w-2xl text-balance leading-relaxed">
            9 tabelas. 2 anos de dados reais do maior marketplace brasileiro.
            Um pipeline completo — do SQL analítico no DuckDB, passando por
            estatística e machine learning em Python, até visualização interativa
            em Next.js. Cada capítulo abaixo é uma pergunta de negócio
            respondida com dados.
          </p>

          {/* Stats */}
          <dl className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-4 sm:gap-6">
            {STATS.map(({ value, label }) => (
              <div
                key={label}
                className="bg-white border border-border rounded px-4 py-4"
              >
                <dt className="font-sans text-xs text-muted uppercase tracking-wide">
                  {label}
                </dt>
                <dd className="font-serif text-2xl sm:text-3xl font-bold text-primary mt-1">
                  {value}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Chapter grid */}
      <section className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="font-serif text-2xl sm:text-3xl font-bold text-primary mb-2">
          Capítulos
        </h2>
        <p className="font-sans text-sm text-muted mb-8">
          Seis perguntas de negócio, seis análises independentes com
          visualizações interativas e narrativa editorial.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {CHAPTER_ORDER.map((slug) => {
            const meta = CHAPTER_META[slug];
            return (
              <Link
                key={slug}
                href={`/${slug}`}
                className="group block bg-white border border-border rounded p-5 hover:border-accent transition-colors"
              >
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className="font-serif text-3xl font-bold text-secondary leading-none">
                    {meta.num}
                  </span>
                  <span className="font-sans text-xs text-muted group-hover:text-accent transition-colors mt-1">
                    ver capítulo →
                  </span>
                </div>
                <h3 className="font-serif text-lg font-semibold text-primary mb-2">
                  {CHAPTER_TITLES[slug]}
                </h3>
                <p className="font-sans text-sm text-muted leading-relaxed mb-4">
                  {meta.description}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {meta.tecnicas.map((t) => (
                    <TechBadge key={t} label={t} />
                  ))}
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Sobre */}
      <section className="border-t border-border bg-surface">
        <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-primary mb-6">
            Sobre o projeto
          </h2>
          <div className="max-w-3xl space-y-4 font-sans text-base text-foreground leading-relaxed">
            <p>
              O dataset <strong>Olist Brazilian E-Commerce</strong> é público,
              real e tem 99.441 pedidos realizados entre setembro de 2016 e
              outubro de 2018 no maior marketplace brasileiro. São 9 tabelas
              relacionais com informações de pedidos, produtos, clientes,
              vendedores, pagamentos e avaliações.
            </p>
            <p>
              Este projeto demonstra o pipeline completo de um analista de dados:
              ingestão dos CSVs no DuckDB, queries SQL analíticas para extrair
              indicadores de cada capítulo, análises em Python com testes de
              hipótese, clustering K-Means e modelo preditivo, e por fim a
              visualização interativa neste dashboard. Todo o código é testado,
              documentado e reproduzível.
            </p>
            <p>
              O objetivo não é apenas mostrar gráficos — é contar a história
              que os dados revelam sobre o e-commerce brasileiro: onde estão os
              gargalos, quem são os clientes, o que determina a satisfação e
              como o tempo e a geografia moldam o consumo online no Brasil.
            </p>
          </div>
        </div>
      </section>

      {/* Skills */}
      <section className="border-t border-border">
        <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-primary mb-8">
            Skills demonstradas
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {SKILLS.map(({ area, items }) => (
              <div key={area}>
                <h3 className="font-sans text-xs font-semibold text-muted uppercase tracking-widest mb-3">
                  {area}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {items.map((item) => (
                    <TechBadge key={item} label={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
