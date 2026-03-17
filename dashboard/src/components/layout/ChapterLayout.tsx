import TechBadge from "@/components/editorial/TechBadge";

interface ChapterLayoutProps {
  title: string;
  subtitle?: string;
  tecnicas?: string[];
  children: React.ReactNode;
}

/**
 * Template base para todos os capítulos do dashboard.
 *
 * Estrutura: título serif + subtítulo + badges de técnicas + conteúdo.
 */
const ChapterLayout = ({
  title,
  subtitle,
  tecnicas,
  children,
}: ChapterLayoutProps) => (
  <article className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <header className="mb-8 border-b border-border pb-6">
      <h1 className="font-serif text-3xl sm:text-4xl font-bold text-primary text-balance">
        {title}
      </h1>
      {subtitle && (
        <p className="mt-3 font-sans text-lead text-muted text-balance">
          {subtitle}
        </p>
      )}
      {tecnicas && tecnicas.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {tecnicas.map((t) => (
            <TechBadge key={t} label={t} />
          ))}
        </div>
      )}
    </header>
    <div className="space-y-10">{children}</div>
  </article>
);

export default ChapterLayout;
