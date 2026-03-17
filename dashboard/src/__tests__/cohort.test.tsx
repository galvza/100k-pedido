/**
 * Testes dos componentes do capítulo Cohort Analysis — T078.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type { CohortHeatmap as CohortHeatmapData, CohortRecompra } from "@/types";

vi.mock("@/lib/data", () => ({
  loadChapterData: vi.fn(),
}));

import CohortHeatmap from "@/components/charts/CohortHeatmap";
import RetentionSummary from "@/components/charts/RetentionSummary";
import { loadChapterData } from "@/lib/data";

// ------------------------------------------------------------------ //
// Fixtures
// ------------------------------------------------------------------ //

const heatmapFixture: CohortHeatmapData = {
  coortes: ["2017-01", "2017-02", "2017-03"],
  periodos: [0, 1, 2, 3],
  dados: [
    { coorte: "2017-01", tamanho: 1120, retencao: [1.0, 0.062, 0.036, 0.021] },
    { coorte: "2017-02", tamanho: 1240, retencao: [1.0, 0.058, 0.032, null] },
    { coorte: "2017-03", tamanho: 1380, retencao: [1.0, 0.054, null, null] },
  ],
};

const recompraFixture: CohortRecompra = {
  total_clientes: 96461,
  clientes_recompra: 6717,
  taxa_recompra_pct: 6.97,
  media_pedidos_por_cliente: 1.07,
  dias_medio_ate_recompra: 183,
};

const mockLoad = vi.mocked(loadChapterData);

// ------------------------------------------------------------------ //
// T078 — CohortHeatmap
// ------------------------------------------------------------------ //

describe("T078 — CohortHeatmap", () => {
  beforeEach(() => vi.clearAllMocks());

  it("T078a: exibe skeleton enquanto carrega", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<CohortHeatmap />);
    expect(screen.getByTestId("cohort-heatmap-loading")).toBeInTheDocument();
  });

  it("T078b: renderiza tabela após carregar dados", async () => {
    mockLoad.mockResolvedValue(heatmapFixture);
    render(<CohortHeatmap />);
    await waitFor(() =>
      expect(screen.getByTestId("cohort-heatmap")).toBeInTheDocument()
    );
  });

  it("T078c: período M+0 exibe 100,0% (retenção total)", async () => {
    mockLoad.mockResolvedValue(heatmapFixture);
    render(<CohortHeatmap />);
    await waitFor(() => {
      const cells = screen.getAllByText("100,0%");
      expect(cells.length).toBe(3); // uma por coorte
    });
  });

  it("T078d: células null não exibem texto", async () => {
    mockLoad.mockResolvedValue(heatmapFixture);
    render(<CohortHeatmap />);
    await waitFor(() =>
      expect(screen.getByTestId("cohort-heatmap")).toBeInTheDocument()
    );
    // O fixture tem 3 células null; verificar que os valores não aparecem como texto
    const allCells = document.querySelectorAll("td");
    const emptyCells = Array.from(allCells).filter(
      (td) => td.textContent === "" && td.style.backgroundColor === "rgb(243, 244, 246)"
    );
    expect(emptyCells.length).toBe(3);
  });

  it("T078e: exibe rótulos de coorte formatados (Jan 2017)", async () => {
    mockLoad.mockResolvedValue(heatmapFixture);
    render(<CohortHeatmap />);
    await waitFor(() =>
      expect(screen.getByText("Jan 2017")).toBeInTheDocument()
    );
  });

  it("T078f: exibe mensagem para dados vazios", async () => {
    mockLoad.mockResolvedValue({ coortes: [], periodos: [], dados: [] });
    render(<CohortHeatmap />);
    await waitFor(() =>
      expect(screen.getByText(/sem dados/i)).toBeInTheDocument()
    );
  });

  it("T078g: chama loadChapterData com o arquivo correto", async () => {
    mockLoad.mockResolvedValue(heatmapFixture);
    render(<CohortHeatmap />);
    await waitFor(() =>
      expect(mockLoad).toHaveBeenCalledWith("03_cohort_heatmap.json")
    );
  });
});

// ------------------------------------------------------------------ //
// T078 — RetentionSummary
// ------------------------------------------------------------------ //

describe("T078 — RetentionSummary", () => {
  beforeEach(() => vi.clearAllMocks());

  it("T078h: exibe skeleton enquanto carrega", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<RetentionSummary />);
    expect(screen.getByTestId("retention-summary-loading")).toBeInTheDocument();
  });

  it("T078i: renderiza cards após carregar dados", async () => {
    mockLoad.mockResolvedValue(recompraFixture);
    render(<RetentionSummary />);
    await waitFor(() =>
      expect(screen.getByTestId("retention-summary")).toBeInTheDocument()
    );
  });

  it("T078j: exibe taxa de recompra formatada", async () => {
    mockLoad.mockResolvedValue(recompraFixture);
    render(<RetentionSummary />);
    await waitFor(() => {
      // formatPercent(6.97/100) = "7,0%"
      const pctCells = screen.getAllByText("7,0%");
      expect(pctCells.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("T078k: exibe tempo médio de recompra", async () => {
    mockLoad.mockResolvedValue(recompraFixture);
    render(<RetentionSummary />);
    await waitFor(() =>
      expect(screen.getByText("183 dias")).toBeInTheDocument()
    );
  });

  it("T078l: exibe '—' quando dias_medio_ate_recompra é null", async () => {
    mockLoad.mockResolvedValue({ ...recompraFixture, dias_medio_ate_recompra: null });
    render(<RetentionSummary />);
    await waitFor(() =>
      expect(screen.getByText("—")).toBeInTheDocument()
    );
  });
});
