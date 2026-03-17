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
      "Do primeiro clique à entrega: taxas de conversão em cada etapa do processo de compra.",
    tecnicas: ["JOINs", "CTEs", "Funil de conversão"],
  },
  rfm: {
    num: "02",
    description:
      "Segmentação comportamental por Recência, Frequência e Valor monetário dos clientes.",
    tecnicas: ["Window Functions", "K-Means", "Clustering"],
  },
  cohort: {
    num: "03",
    description:
      "Clientes que compraram no mesmo mês retornam? Análise de retenção cohort a cohort.",
    tecnicas: ["CTEs aninhadas", "Pivot", "Retenção"],
  },
  geografico: {
    num: "04",
    description:
      "Como vendas, frete e satisfação variam entre os 27 estados brasileiros.",
    tecnicas: ["GROUP BY", "Correlação", "Geoespacial"],
  },
  sazonalidade: {
    num: "05",
    description:
      "Padrões temporais de demanda: tendência, sazonalidade e ciclos semanais.",
    tecnicas: ["DATE_TRUNC", "Decomposição sazonal", "Série temporal"],
  },
  reviews: {
    num: "06",
    description:
      "O que determina a nota do cliente? Atraso na entrega, categoria e sentimento textual.",
    tecnicas: ["STRING_AGG", "Análise de texto", "Testes de hipótese"],
  },
};

const STATS = [
  { value: "~100k", label: "pedidos analisados" },
  { value: "9", label: "tabelas relacionais" },
  { value: "6", label: "capítulos analíticos" },
  { value: "2016–2018", label: "período coberto" },
];

const SKILLS = [
  {
    area: "SQL",
    items: ["DuckDB", "JOINs complexos", "CTEs", "Window Functions", "Agregações"],
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
            Projeto de portfólio
          </p>
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-bold text-primary text-balance leading-tight">
            100k Pedidos
          </h1>
          <p className="font-serif text-xl sm:text-2xl text-muted mt-3 text-balance">
            Raio-X do E-commerce Brasileiro
          </p>
          <p className="font-sans text-base text-muted mt-6 max-w-2xl text-balance leading-relaxed">
            Pipeline completo de análise de dados usando 100 mil pedidos reais
            do marketplace Olist. SQL analítico no DuckDB, estatística e ML em
            Python, e visualização interativa em Next.js com Recharts.
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
          Cada capítulo é uma análise independente com visualizações interativas.
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
              O dataset <strong>Olist Brazilian E-Commerce</strong> contém 9
              tabelas relacionais com informações de pedidos, produtos,
              clientes, vendedores, pagamentos e reviews de um marketplace
              brasileiro real entre setembro de 2016 e outubro de 2018.
            </p>
            <p>
              O pipeline começa com a ingestão dos CSVs no DuckDB, onde queries
              SQL analíticas extraem os indicadores de cada capítulo. Em
              seguida, análises em Python aplicam estatística descritiva, testes
              de hipótese, clustering K-Means e um modelo preditivo de atraso em
              Logistic Regression e Random Forest. Os resultados são exportados
              como JSONs estáticos consumidos por este dashboard.
            </p>
            <p>
              O objetivo é demonstrar o pipeline completo de um projeto de dados
              — da engenharia de dados à visualização final — com código
              testado, documentado e reproducível.
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
