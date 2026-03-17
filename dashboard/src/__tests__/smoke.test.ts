import { describe, expect, it } from "vitest";

import funilConversao from "./fixtures/01_funil_conversao.json";
import rfmSegmentos from "./fixtures/02_rfm_segmentos.json";
import cohortHeatmap from "./fixtures/03_cohort_heatmap.json";
import geoEstados from "./fixtures/04_geo_estados.json";
import sazonalidadeMensal from "./fixtures/05_sazonalidade_mensal.json";
import reviewsDistribuicao from "./fixtures/06_reviews_distribuicao.json";

describe("Smoke test — setup do Vitest", () => {
  it("ambiente jsdom disponivel", () => {
    expect(document).toBeDefined();
    expect(window).toBeDefined();
  });

  it("jest-dom matchers funcionam", () => {
    const div = document.createElement("div");
    div.textContent = "teste";
    document.body.appendChild(div);
    expect(div).toBeInTheDocument();
    document.body.removeChild(div);
  });
});

describe("Fixtures JSON sao validas e parseiaveis", () => {
  it("01_funil_conversao.json — 4 etapas do funil", () => {
    expect(funilConversao).toHaveLength(4);
    for (const etapa of funilConversao) {
      expect(etapa).toHaveProperty("etapa");
      expect(etapa).toHaveProperty("pedidos");
      expect(etapa).toHaveProperty("taxa_conversao");
      expect(etapa).toHaveProperty("tempo_medio_dias");
    }
  });

  it("02_rfm_segmentos.json — 5 segmentos RFM", () => {
    expect(rfmSegmentos).toHaveLength(5);
    for (const seg of rfmSegmentos) {
      expect(seg).toHaveProperty("segmento");
      expect(seg).toHaveProperty("contagem");
      expect(seg).toHaveProperty("percentual");
      expect(seg).toHaveProperty("recencia_media");
      expect(seg).toHaveProperty("frequencia_media");
      expect(seg).toHaveProperty("monetario_medio");
    }
  });

  it("03_cohort_heatmap.json — 3 coortes x 4 periodos", () => {
    expect(cohortHeatmap.coortes).toHaveLength(3);
    expect(cohortHeatmap.periodos).toHaveLength(4);
    expect(cohortHeatmap.dados).toHaveLength(3);
    for (const coorte of cohortHeatmap.dados) {
      expect(coorte).toHaveProperty("coorte");
      expect(coorte).toHaveProperty("tamanho");
      expect(coorte.retencao).toHaveLength(4);
    }
  });

  it("04_geo_estados.json — 10 estados com metricas", () => {
    expect(geoEstados).toHaveLength(10);
    for (const estado of geoEstados) {
      expect(estado).toHaveProperty("estado");
      expect(estado).toHaveProperty("pedidos");
      expect(estado).toHaveProperty("receita");
      expect(estado).toHaveProperty("ticket_medio");
      expect(estado).toHaveProperty("frete_medio");
      expect(estado).toHaveProperty("review_score_medio");
    }
  });

  it("05_sazonalidade_mensal.json — 12 meses", () => {
    expect(sazonalidadeMensal).toHaveLength(12);
    for (const mes of sazonalidadeMensal) {
      expect(mes).toHaveProperty("mes");
      expect(mes).toHaveProperty("pedidos");
      expect(mes).toHaveProperty("receita");
      expect(mes).toHaveProperty("media_movel_3m");
    }
  });

  it("06_reviews_distribuicao.json — scores 1 a 5", () => {
    expect(reviewsDistribuicao).toHaveLength(5);
    const scores = reviewsDistribuicao.map((r) => r.score);
    expect(scores).toEqual([1, 2, 3, 4, 5]);
    for (const review of reviewsDistribuicao) {
      expect(review).toHaveProperty("contagem");
      expect(review).toHaveProperty("percentual");
    }
  });
});
