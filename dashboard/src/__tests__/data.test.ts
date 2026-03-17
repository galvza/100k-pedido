/**
 * Testes da função loadChapterData — T071-T075.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { loadChapterData } from "@/lib/data";
import type { FunilConversao } from "@/types";

// Utilitário: cria um Response-like mockado
const mockResponse = (body: unknown, ok = true) => ({
  ok,
  status: ok ? 200 : 404,
  json: vi.fn().mockResolvedValue(body),
});

const mockErrorResponse = () => ({
  ok: true,
  status: 200,
  json: vi.fn().mockRejectedValue(new Error("JSON parse error")),
});

describe("loadChapterData", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  // ---------------------------------------------------------------- //
  // T071 — caminho feliz
  // ---------------------------------------------------------------- //

  it("T071: carrega e retorna array do JSON corretamente", async () => {
    const fixture: FunilConversao[] = [
      { etapa: "Compra", pedidos: 200, taxa_conversao: 1.0, tempo_medio_dias: 0 },
      { etapa: "Entrega", pedidos: 159, taxa_conversao: 0.93, tempo_medio_dias: 12.34 },
    ];

    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse(fixture) as unknown as Response
    );

    const result = await loadChapterData<FunilConversao[]>(
      "01_funil_conversao.json"
    );

    expect(result).toEqual(fixture);
    expect(result).toHaveLength(2);
    expect(result[0].etapa).toBe("Compra");
  });

  it("T071b: chama fetch com o caminho correto (/data/filename)", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse([]) as unknown as Response
    );

    await loadChapterData("05_sazonalidade_mensal.json");

    expect(fetch).toHaveBeenCalledWith("/data/05_sazonalidade_mensal.json");
  });

  // ---------------------------------------------------------------- //
  // T072 — JSON malformado → fallback
  // ---------------------------------------------------------------- //

  it("T072: retorna fallback vazio quando JSON está malformado", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockErrorResponse() as unknown as Response
    );

    const result = await loadChapterData("malformed.json");

    expect(result).toEqual([]);
  });

  // ---------------------------------------------------------------- //
  // T073 — HTTP 404 → fallback
  // ---------------------------------------------------------------- //

  it("T073: retorna fallback vazio para resposta 404", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse(null, false) as unknown as Response
    );

    const result = await loadChapterData("missing.json");

    expect(result).toEqual([]);
  });

  // ---------------------------------------------------------------- //
  // T074 — erro de rede → fallback
  // ---------------------------------------------------------------- //

  it("T074: retorna fallback vazio quando fetch lança exceção", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

    const result = await loadChapterData("error.json");

    expect(result).toEqual([]);
  });

  // ---------------------------------------------------------------- //
  // T075 — fallback customizado
  // ---------------------------------------------------------------- //

  it("T075: usa fallback customizado quando fornecido", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

    const fallback = { coortes: [], periodos: [], dados: [] };
    const result = await loadChapterData("03_cohort_heatmap.json", fallback);

    expect(result).toBe(fallback);
  });

  it("T075b: tipo genérico é inferido corretamente pelo TypeScript", async () => {
    const fixture = { score: 5, contagem: 70, percentual: 35.0 };
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse(fixture) as unknown as Response
    );

    // O tipo é inferido como ReviewsDistribuicao sem cast explícito
    const result = await loadChapterData<typeof fixture>(
      "06_reviews_distribuicao.json"
    );

    expect(result.score).toBe(5);
    expect(result.percentual).toBe(35.0);
  });
});
