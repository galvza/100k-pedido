/**
 * Constantes globais do dashboard: cores, títulos, configurações de gráfico.
 */

/** Seis cores editoriais pra séries de dados em gráficos. Sem gradientes. */
export const CHART_COLORS = [
  "#2563EB", // azul
  "#059669", // verde
  "#D97706", // âmbar
  "#DC2626", // vermelho
  "#7C3AED", // violeta
  "#0891B2", // ciano
] as const;

/** Mapeamento de slug de rota → título em PT-BR. */
export const CHAPTER_TITLES: Record<string, string> = {
  funil: "Funil de Vendas",
  rfm: "Segmentação RFM",
  cohort: "Análise de Cohort",
  geografico: "Análise Geográfica",
  sazonalidade: "Sazonalidade",
  reviews: "Reviews e Satisfação",
};

/** Configurações padrão pra gráficos Recharts. */
export const CHART_CONFIG = {
  margin: { top: 8, right: 16, bottom: 8, left: 16 },
  marginWithAxis: { top: 8, right: 24, bottom: 40, left: 56 },
  fontSize: 12,
  fontSizeAxis: 11,
  strokeWidth: 2,
  dotRadius: 4,
  barRadius: 2,
  animationDuration: 400,
} as const;

/** Ordem de exibição dos capítulos na navegação. */
export const CHAPTER_ORDER = [
  "funil",
  "rfm",
  "cohort",
  "geografico",
  "sazonalidade",
  "reviews",
] as const;

/** Cor de fundo neutra pra tooltips e cards. */
export const SURFACE_COLOR = "#F9F9F7";

/** Cor de texto muted pra labels e eixos. */
export const MUTED_COLOR = "#6B7280";
