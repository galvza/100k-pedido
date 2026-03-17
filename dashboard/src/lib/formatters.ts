/**
 * Formatadores de valores para o padrão brasileiro (PT-BR).
 *
 * Todas as funções retornam "—" (em-dash) para valores nulos,
 * undefined ou NaN, nunca lançam exceções.
 */

import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";

/** Marcador padrão para valor ausente. */
export const VALOR_VAZIO = "—";

/**
 * Formata valor monetário em reais (R$ 1.234,56).
 *
 * @param valor - Número ou null/undefined
 */
export const formatBRL = (valor: number | null | undefined): string => {
  if (valor == null || !isFinite(valor) || isNaN(valor)) return VALOR_VAZIO;
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
    .format(valor)
    .replace(/\u00a0/g, " "); // normaliza espaço não-quebrável → espaço regular
};

/**
 * Formata valor monetário em notação compacta (R$ 1,5M, R$ 23,4k).
 *
 * Usa sufixos M (milhão) e k (mil) para facilitar leitura em gráficos.
 *
 * @param valor - Número ou null/undefined
 */
export const formatBRLCompact = (valor: number | null | undefined): string => {
  if (valor == null || !isFinite(valor) || isNaN(valor)) return VALOR_VAZIO;
  const abs = Math.abs(valor);
  if (abs >= 1_000_000) {
    const v = new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(valor / 1_000_000);
    return `R$ ${v}M`;
  }
  if (abs >= 1_000) {
    const v = new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(valor / 1_000);
    return `R$ ${v}k`;
  }
  return formatBRL(valor);
};

/**
 * Formata proporção decimal como percentual (0.8543 → "85,4%").
 *
 * Recebe valor entre 0 e 1. Para valores já em percentual (ex: 85.4),
 * divida por 100 antes de chamar esta função.
 *
 * @param valor    - Número entre 0 e 1, ou null/undefined
 * @param decimals - Casas decimais (padrão: 1)
 */
export const formatPercent = (
  valor: number | null | undefined,
  decimals = 1
): string => {
  if (valor == null || !isFinite(valor) || isNaN(valor)) return VALOR_VAZIO;
  const pct = valor * 100;
  return (
    new Intl.NumberFormat("pt-BR", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(pct) + "%"
  );
};

/**
 * Formata data ISO (YYYY-MM-DD) no padrão brasileiro (15/06/2017).
 *
 * @param iso - String ISO ou null/undefined
 */
export const formatDate = (iso: string | null | undefined): string => {
  if (!iso) return VALOR_VAZIO;
  try {
    return format(parseISO(iso), "dd/MM/yyyy");
  } catch {
    return VALOR_VAZIO;
  }
};

/**
 * Formata mês-ano (YYYY-MM) no padrão "Jun 2017".
 *
 * Aceita tanto "YYYY-MM" quanto "YYYY-MM-DD".
 *
 * @param iso - String YYYY-MM ou YYYY-MM-DD, ou null/undefined
 */
export const formatMonthYear = (iso: string | null | undefined): string => {
  if (!iso) return VALOR_VAZIO;
  try {
    // Completa pra YYYY-MM-DD se necessário
    const normalized = iso.length === 7 ? `${iso}-01` : iso;
    const date = parseISO(normalized);
    const formatted = format(date, "MMM yyyy", { locale: ptBR });
    // Capitaliza primeira letra (jun → Jun)
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
  } catch {
    return VALOR_VAZIO;
  }
};

/**
 * Formata número inteiro com separador de milhar brasileiro (99.441).
 *
 * @param valor - Número inteiro ou null/undefined
 */
export const formatNumber = (valor: number | null | undefined): string => {
  if (valor == null || !isFinite(valor) || isNaN(valor)) return VALOR_VAZIO;
  return new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 0,
  }).format(valor);
};
