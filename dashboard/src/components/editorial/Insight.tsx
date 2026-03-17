interface InsightProps {
  children: React.ReactNode;
  /** Emoji ou caractere pra destacar o insight (ex: "📌", "↑") */
  icon?: string;
}

/**
 * Caixa de destaque editorial para insights quantitativos.
 * Inspirado nos call-outs do Nexo Jornal e Our World in Data.
 */
const Insight = ({ children, icon = "→" }: InsightProps) => (
  <aside className="my-6 border-l-4 border-accent pl-4 py-2">
    <p className="font-sans text-sm leading-relaxed text-foreground">
      <span className="mr-2 text-accent" aria-hidden="true">
        {icon}
      </span>
      {children}
    </p>
  </aside>
);

export default Insight;
