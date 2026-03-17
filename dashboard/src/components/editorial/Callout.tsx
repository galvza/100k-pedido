type CalloutVariant = "info" | "warning" | "note";

interface CalloutProps {
  children: React.ReactNode;
  variant?: CalloutVariant;
  title?: string;
}

const VARIANT_STYLES: Record<CalloutVariant, string> = {
  info: "bg-blue-50 border-chart-1 text-blue-900",
  warning: "bg-amber-50 border-chart-3 text-amber-900",
  note: "bg-surface border-border text-foreground",
};

const VARIANT_LABELS: Record<CalloutVariant, string> = {
  info: "Nota",
  warning: "Atenção",
  note: "Contexto",
};

/**
 * Nota lateral com contexto metodológico ou limitação da análise.
 */
const Callout = ({ children, variant = "note", title }: CalloutProps) => (
  <aside
    className={`my-4 rounded border-l-4 px-4 py-3 text-sm font-sans ${VARIANT_STYLES[variant]}`}
    role="note"
  >
    <p className="font-semibold mb-1">{title ?? VARIANT_LABELS[variant]}</p>
    <div className="leading-relaxed">{children}</div>
  </aside>
);

export default Callout;
