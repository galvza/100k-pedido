interface TechBadgeProps {
  label: string;
}

const TechBadge = ({ label }: TechBadgeProps) => (
  <span className="inline-block px-2 py-0.5 text-xs font-sans font-medium bg-secondary text-muted rounded border border-border">
    {label}
  </span>
);

export default TechBadge;
