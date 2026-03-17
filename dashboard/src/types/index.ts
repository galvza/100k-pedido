/**
 * Interfaces TypeScript para todos os formatos de JSON gerados pelo pipeline.
 * Refletem exatamente as estruturas definidas em pipeline/export.py.
 */

// ------------------------------------------------------------------ //
// Cap. 1 — Funil de Vendas
// ------------------------------------------------------------------ //

export interface FunilStatus {
  status: string;
  contagem: number;
  percentual: number;
}

export interface FunilConversao {
  etapa: string;
  pedidos: number;
  taxa_conversao: number;
  tempo_medio_dias: number;
}

export interface FunilTempos {
  faixa: string;
  contagem: number;
  media_dias_na_faixa: number;
  min_dias: number;
  max_dias: number;
}

// ------------------------------------------------------------------ //
// Cap. 2 — Segmentação RFM
// ------------------------------------------------------------------ //

export interface RfmDimStats {
  min: number;
  max: number;
  media: number;
  mediana: number;
  std: number;
  q1: number;
  q3: number;
}

export interface RfmDistribuicao {
  recency: RfmDimStats;
  frequency: RfmDimStats;
  monetary: RfmDimStats;
}

export interface RfmSegmento {
  segmento: string;
  contagem: number;
  percentual: number;
  recencia_media: number;
  frequencia_media: number;
  monetario_medio: number;
  r_score_medio: number;
  f_score_medio: number;
  m_score_medio: number;
}

export interface RfmClusteringItem {
  k: number;
  inertia: number;
}

export interface RfmSilhouetteItem {
  k: number;
  silhouette: number;
}

export interface RfmClustering {
  k_otimo: number | null;
  n_original: number;
  n_usado: number;
  elbow: RfmClusteringItem[];
  silhouette: RfmSilhouetteItem[];
  centroids?: number[][];
}

// ------------------------------------------------------------------ //
// Cap. 3 — Cohort Analysis
// ------------------------------------------------------------------ //

export interface CohortHeatmapDado {
  coorte: string;
  tamanho: number;
  retencao: Array<number | null>;
}

export interface CohortHeatmap {
  coortes: string[];
  periodos: number[];
  dados: CohortHeatmapDado[];
}

export interface CohortRecompra {
  total_clientes: number;
  clientes_recompra: number;
  taxa_recompra_pct: number;
  media_pedidos_por_cliente: number;
  dias_medio_ate_recompra: number | null;
}

// ------------------------------------------------------------------ //
// Cap. 4 — Análise Geográfica
// ------------------------------------------------------------------ //

export interface GeoEstado {
  estado: string;
  pedidos: number;
  receita: number;
  ticket_medio: number;
  frete_medio: number;
  frete_percentual: number;
  review_score_medio: number;
  total_vendedores: number;
}

export interface GeoCategoria {
  estado: string;
  categoria: string;
  pedidos: number;
  receita: number;
}

export interface GeoCorrelacao {
  teste_usado: string;
  p_value: number;
  significativo: boolean;
  tamanho_efeito: number;
  mensagem?: string | null;
}

// ------------------------------------------------------------------ //
// Cap. 5 — Sazonalidade
// ------------------------------------------------------------------ //

export interface SazonalidadeMensal {
  mes: string;
  pedidos: number;
  receita: number;
  media_movel_3m: number | null;
  mom_growth?: number | null;
}

export interface SazonalidadeSemanal {
  dia_semana: number;
  pedidos_medio: number;
  receita_media: number;
  ticket_medio: number;
}

export interface SazonalidadeHoraria {
  hora: number;
  pedidos: number;
  receita: number;
}

// ------------------------------------------------------------------ //
// Cap. 6 — Reviews e Satisfação
// ------------------------------------------------------------------ //

export interface ReviewsDistribuicao {
  score: number;
  contagem: number;
  percentual: number;
}

export interface ReviewsCategorias {
  categoria: string;
  total_reviews: number;
  score_medio: number;
  reviews_positivas: number;
  reviews_negativas: number;
}

export interface ReviewsAtraso {
  faixa_atraso: string;
  contagem: number;
  score_medio: number;
  min_dias: number;
  max_dias: number;
}

export interface ReviewsPalavras {
  palavra: string;
  contagem: number;
  faixa: string;
}
