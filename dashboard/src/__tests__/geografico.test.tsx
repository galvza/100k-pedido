/**
 * Testes dos componentes do capítulo Análise Geográfica — T079.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type { GeoEstado, GeoCorrelacao } from "@/types";

// ------------------------------------------------------------------ //
// Mocks
// ------------------------------------------------------------------ //

vi.mock("@/lib/data", () => ({
  loadChapterData: vi.fn(),
}));

vi.mock("next/dynamic", () => ({
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  default: (_importFn: unknown) => {
    const MockMap = () => <div data-testid="brazil-map-dynamic" />;
    return MockMap;
  },
}));

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  ScatterChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="scatter-chart">{children}</div>
  ),
  Scatter: ({ children }: { children?: React.ReactNode }) => <>{children}</>,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  Label: () => null,
  LabelList: () => null,
  ReferenceLine: () => null,
}));

import BrazilMapWrapper from "@/components/charts/BrazilMapWrapper";
import StateRanking from "@/components/charts/StateRanking";
import CorrelationChart from "@/components/charts/CorrelationChart";
import { loadChapterData } from "@/lib/data";

// ------------------------------------------------------------------ //
// Fixtures
// ------------------------------------------------------------------ //

const estadosFixture: GeoEstado[] = [
  {
    estado: "SP",
    pedidos: 41746,
    receita: 5732456.78,
    ticket_medio: 137.32,
    frete_medio: 15.12,
    frete_percentual: 0.11,
    review_score_medio: 4.07,
    total_vendedores: 1849,
  },
  {
    estado: "RJ",
    pedidos: 12852,
    receita: 1841234.56,
    ticket_medio: 143.27,
    frete_medio: 18.95,
    frete_percentual: 0.132,
    review_score_medio: 4.04,
    total_vendedores: 268,
  },
  {
    estado: "AM",
    pedidos: 748,
    receita: 93567.89,
    ticket_medio: 125.09,
    frete_medio: 53.45,
    frete_percentual: 0.427,
    review_score_medio: 3.52,
    total_vendedores: 4,
  },
];

const correlacaoFixture: GeoCorrelacao = {
  teste_usado: "Spearman",
  p_value: 0.0021,
  significativo: true,
  tamanho_efeito: -0.681,
  mensagem: "Correlação negativa significativa.",
};

const mockLoad = vi.mocked(loadChapterData);

// ------------------------------------------------------------------ //
// T079 — BrazilMapWrapper
// ------------------------------------------------------------------ //

describe("T079 — BrazilMapWrapper", () => {
  beforeEach(() => vi.clearAllMocks());

  it("T079a: exibe skeleton enquanto carrega", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<BrazilMapWrapper />);
    expect(screen.getByTestId("brazil-map-wrapper-loading")).toBeInTheDocument();
  });

  it("T079b: renderiza wrapper após carregar dados", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<BrazilMapWrapper />);
    await waitFor(() =>
      expect(screen.getByTestId("brazil-map-wrapper")).toBeInTheDocument()
    );
  });

  it("T079c: exibe seletor com 3 métricas", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<BrazilMapWrapper />);
    await waitFor(() => {
      expect(screen.getByText("Pedidos")).toBeInTheDocument();
      expect(screen.getByText("Receita (R$)")).toBeInTheDocument();
      expect(screen.getByText("Satisfação")).toBeInTheDocument();
    });
  });

  it("T079d: chama loadChapterData com arquivo correto", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<BrazilMapWrapper />);
    await waitFor(() =>
      expect(mockLoad).toHaveBeenCalledWith("04_geo_estados.json")
    );
  });
});

// ------------------------------------------------------------------ //
// T079 — StateRanking
// ------------------------------------------------------------------ //

describe("T079 — StateRanking", () => {
  beforeEach(() => vi.clearAllMocks());

  it("T079e: exibe skeleton enquanto carrega", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<StateRanking />);
    expect(screen.getByTestId("state-ranking-loading")).toBeInTheDocument();
  });

  it("T079f: renderiza tabela após carregar dados", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<StateRanking />);
    await waitFor(() =>
      expect(screen.getByTestId("state-ranking")).toBeInTheDocument()
    );
  });

  it("T079g: exibe estado SP no ranking", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<StateRanking />);
    await waitFor(() => expect(screen.getByText("SP")).toBeInTheDocument());
  });

  it("T079h: pedidos de SP exibidos formatados", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<StateRanking />);
    await waitFor(() =>
      expect(screen.getByText("41.746")).toBeInTheDocument()
    );
  });

  it("T079i: exibe headers de ordenação clicáveis", async () => {
    mockLoad.mockResolvedValue(estadosFixture);
    render(<StateRanking />);
    await waitFor(() => {
      const headers = screen.getAllByRole("columnheader");
      const labels = headers.map((h) => h.textContent?.replace(/ [↓↑]/, ""));
      expect(labels).toContain("Pedidos");
      expect(labels).toContain("Receita");
      expect(labels).toContain("Frete Médio");
      expect(labels).toContain("Score");
    });
  });
});

// ------------------------------------------------------------------ //
// T079 — CorrelationChart
// ------------------------------------------------------------------ //

describe("T079 — CorrelationChart", () => {
  beforeEach(() => vi.clearAllMocks());

  it("T079j: exibe skeleton enquanto carrega", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<CorrelationChart />);
    expect(
      screen.getByTestId("correlation-chart-loading")
    ).toBeInTheDocument();
  });

  it("T079k: renderiza chart após carregar dados", async () => {
    mockLoad
      .mockResolvedValueOnce(estadosFixture)
      .mockResolvedValueOnce(correlacaoFixture);
    render(<CorrelationChart />);
    await waitFor(() =>
      expect(screen.getByTestId("correlation-chart")).toBeInTheDocument()
    );
  });

  it("T079l: exibe nome do teste estatístico (Spearman)", async () => {
    mockLoad
      .mockResolvedValueOnce(estadosFixture)
      .mockResolvedValueOnce(correlacaoFixture);
    render(<CorrelationChart />);
    await waitFor(() =>
      expect(screen.getByText(/Spearman/i)).toBeInTheDocument()
    );
  });

  it("T079m: exibe correlação negativa significativa", async () => {
    mockLoad
      .mockResolvedValueOnce(estadosFixture)
      .mockResolvedValueOnce(correlacaoFixture);
    render(<CorrelationChart />);
    await waitFor(() => {
      const matches = screen.getAllByText(/negativa significativa/i);
      expect(matches.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("T079n: chama loadChapterData com arquivo de correlação", async () => {
    mockLoad
      .mockResolvedValueOnce(estadosFixture)
      .mockResolvedValueOnce(correlacaoFixture);
    render(<CorrelationChart />);
    await waitFor(() =>
      expect(mockLoad).toHaveBeenCalledWith("04_geo_correlacao.json")
    );
  });
});
