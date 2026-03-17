/**
 * Testes dos formatadores PT-BR — T061-T070.
 */

import { describe, expect, it } from "vitest";
import {
  formatBRL,
  formatBRLCompact,
  formatDate,
  formatMonthYear,
  formatNumber,
  formatPercent,
  VALOR_VAZIO,
} from "@/lib/formatters";

// ------------------------------------------------------------------ //
// T061-T064 — formatBRL
// ------------------------------------------------------------------ //

describe("formatBRL", () => {
  it("T061: formata valor positivo em reais", () => {
    expect(formatBRL(1234.56)).toBe("R$ 1.234,56");
  });

  it("T062: formata zero como R$ 0,00", () => {
    expect(formatBRL(0)).toBe("R$ 0,00");
  });

  it("T063: retorna '—' para null", () => {
    expect(formatBRL(null)).toBe(VALOR_VAZIO);
  });

  it("T064: retorna '—' para NaN", () => {
    expect(formatBRL(NaN)).toBe(VALOR_VAZIO);
  });

  it("formata valor negativo corretamente", () => {
    const result = formatBRL(-500);
    expect(result).toContain("500");
    expect(result).toContain("R$");
  });

  it("formata valor sem casas decimais com dois zeros", () => {
    expect(formatBRL(1000)).toBe("R$ 1.000,00");
  });

  it("não contém espaço não-quebrável (\\u00a0)", () => {
    expect(formatBRL(1234.56)).not.toContain("\u00a0");
  });
});

// ------------------------------------------------------------------ //
// T065 — formatBRLCompact
// ------------------------------------------------------------------ //

describe("formatBRLCompact", () => {
  it("T065: formata milhão com sufixo M", () => {
    expect(formatBRLCompact(1_500_000)).toBe("R$ 1,5M");
  });

  it("formata milhar com sufixo k", () => {
    expect(formatBRLCompact(23_400)).toBe("R$ 23,4k");
  });

  it("usa formatBRL para valores pequenos (< 1000)", () => {
    expect(formatBRLCompact(500)).toBe("R$ 500,00");
  });

  it("retorna '—' para null", () => {
    expect(formatBRLCompact(null)).toBe(VALOR_VAZIO);
  });

  it("retorna '—' para NaN", () => {
    expect(formatBRLCompact(NaN)).toBe(VALOR_VAZIO);
  });
});

// ------------------------------------------------------------------ //
// T066-T067 — formatPercent
// ------------------------------------------------------------------ //

describe("formatPercent", () => {
  it("T066: converte fração decimal em percentual (0.8543 → 85,4%)", () => {
    expect(formatPercent(0.8543)).toBe("85,4%");
  });

  it("T067: retorna '—' para null", () => {
    expect(formatPercent(null)).toBe(VALOR_VAZIO);
  });

  it("retorna '—' para NaN", () => {
    expect(formatPercent(NaN)).toBe(VALOR_VAZIO);
  });

  it("formata 1.0 como 100,0%", () => {
    expect(formatPercent(1.0)).toBe("100,0%");
  });

  it("formata 0 como 0,0%", () => {
    expect(formatPercent(0)).toBe("0,0%");
  });

  it("aceita número de casas decimais customizado", () => {
    expect(formatPercent(0.1234, 2)).toBe("12,34%");
  });
});

// ------------------------------------------------------------------ //
// T068-T069 — formatDate
// ------------------------------------------------------------------ //

describe("formatDate", () => {
  it("T068: formata data ISO no padrão dd/MM/yyyy", () => {
    expect(formatDate("2017-06-15")).toBe("15/06/2017");
  });

  it("T069: retorna '—' para null", () => {
    expect(formatDate(null)).toBe(VALOR_VAZIO);
  });

  it("retorna '—' para string vazia", () => {
    expect(formatDate("")).toBe(VALOR_VAZIO);
  });

  it("retorna '—' para data inválida", () => {
    expect(formatDate("nao-e-data")).toBe(VALOR_VAZIO);
  });

  it("formata corretamente o início do dataset (2016-09-04)", () => {
    expect(formatDate("2016-09-04")).toBe("04/09/2016");
  });
});

// ------------------------------------------------------------------ //
// T070 — formatMonthYear
// ------------------------------------------------------------------ //

describe("formatMonthYear", () => {
  it("T070: formata YYYY-MM como 'Mês Ano' em PT-BR", () => {
    expect(formatMonthYear("2017-06")).toBe("Jun 2017");
  });

  it("retorna '—' para null", () => {
    expect(formatMonthYear(null)).toBe(VALOR_VAZIO);
  });

  it("aceita YYYY-MM-DD e retorna apenas mês/ano", () => {
    expect(formatMonthYear("2018-11-23")).toBe("Nov 2018");
  });

  it("capitaliza a primeira letra do mês", () => {
    const result = formatMonthYear("2017-01");
    expect(result[0]).toBe(result[0].toUpperCase());
  });
});

// ------------------------------------------------------------------ //
// formatNumber
// ------------------------------------------------------------------ //

describe("formatNumber", () => {
  it("formata inteiro com separador de milhar brasileiro (99.441)", () => {
    expect(formatNumber(99441)).toBe("99.441");
  });

  it("formata número pequeno sem separador", () => {
    expect(formatNumber(42)).toBe("42");
  });

  it("retorna '—' para null", () => {
    expect(formatNumber(null)).toBe(VALOR_VAZIO);
  });

  it("retorna '—' para NaN", () => {
    expect(formatNumber(NaN)).toBe(VALOR_VAZIO);
  });
});
