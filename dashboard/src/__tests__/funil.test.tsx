/**
 * Testes dos componentes de gráfico do capítulo Funil — T076.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type { FunilConversao, FunilTempos } from "@/types";

// ------------------------------------------------------------------ //
// Mocks — hoisted por Vitest antes dos imports dos componentes
// ------------------------------------------------------------------ //

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  BarChart: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="bar-chart">{children}</div>
  ),
  Bar: () => <div data-testid="bar" />,
  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
  Cell: () => null,
  LabelList: () => null,
}));

vi.mock("@/lib/data", () => ({
  loadChapterData: vi.fn(),
}));

// Importar APÓS os mocks
import FunnelBar from "@/components/charts/FunnelBar";
import TimelineChart from "@/components/charts/TimelineChart";
import DeliveryHistogram from "@/components/charts/DeliveryHistogram";
import { loadChapterData } from "@/lib/data";

// ------------------------------------------------------------------ //
// Fixtures
// ------------------------------------------------------------------ //

const conversaoFixture: FunilConversao[] = [
  { etapa: "Compra",    pedidos: 99441, taxa_conversao: 1.0,   tempo_medio_dias: 0.0   },
  { etapa: "Aprovação", pedidos: 97671, taxa_conversao: 0.982, tempo_medio_dias: 0.41  },
  { etapa: "Envio",     pedidos: 96585, taxa_conversao: 0.989, tempo_medio_dias: 2.53  },
  { etapa: "Entrega",   pedidos: 96478, taxa_conversao: 0.999, tempo_medio_dias: 12.09 },
];

const temposFixture: FunilTempos[] = [
  { faixa: "0–7 dias",   contagem: 21847, media_dias_na_faixa: 4.82,  min_dias: 0,  max_dias: 7   },
  { faixa: "8–14 dias",  contagem: 38134, media_dias_na_faixa: 10.91, min_dias: 8,  max_dias: 14  },
  { faixa: "15–21 dias", contagem: 22563, media_dias_na_faixa: 17.84, min_dias: 15, max_dias: 21  },
  { faixa: "22–30 dias", contagem: 8912,  media_dias_na_faixa: 25.43, min_dias: 22, max_dias: 30  },
  { faixa: "31–60 dias", contagem: 4122,  media_dias_na_faixa: 42.17, min_dias: 31, max_dias: 60  },
  { faixa: "> 60 dias",  contagem: 900,   media_dias_na_faixa: 87.32, min_dias: 61, max_dias: 210 },
];

const mockLoad = vi.mocked(loadChapterData);

// ------------------------------------------------------------------ //
// T076 — FunnelBar
// ------------------------------------------------------------------ //

describe("T076 — FunnelBar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("T076a: exibe skeleton de carregamento antes dos dados chegarem", () => {
    mockLoad.mockImplementation(() => new Promise(() => {})); // nunca resolve
    render(<FunnelBar />);
    expect(screen.getByTestId("funnel-bar-loading")).toBeInTheDocument();
  });

  it("T076b: renderiza gráfico após carregar dados", async () => {
    mockLoad.mockResolvedValue(conversaoFixture);
    render(<FunnelBar />);
    await waitFor(() =>
      expect(screen.getByTestId("funnel-bar")).toBeInTheDocument()
    );
  });

  it("T076c: exibe mensagem quando dados estão vazios", async () => {
    mockLoad.mockResolvedValue([]);
    render(<FunnelBar />);
    await waitFor(() =>
      expect(screen.getByText(/sem dados/i)).toBeInTheDocument()
    );
  });

  it("T076d: chama loadChapterData com o arquivo correto", async () => {
    mockLoad.mockResolvedValue(conversaoFixture);
    render(<FunnelBar />);
    await waitFor(() => expect(mockLoad).toHaveBeenCalledWith("01_funil_conversao.json"));
  });
});

// ------------------------------------------------------------------ //
// T076 — TimelineChart
// ------------------------------------------------------------------ //

describe("T076 — TimelineChart", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("T076e: exibe skeleton de carregamento antes dos dados chegarem", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<TimelineChart />);
    expect(screen.getByTestId("timeline-chart-loading")).toBeInTheDocument();
  });

  it("T076f: renderiza gráfico após carregar dados", async () => {
    mockLoad.mockResolvedValue(conversaoFixture);
    render(<TimelineChart />);
    await waitFor(() =>
      expect(screen.getByTestId("timeline-chart")).toBeInTheDocument()
    );
  });

  it("T076g: exibe mensagem quando dados estão vazios", async () => {
    mockLoad.mockResolvedValue([]);
    render(<TimelineChart />);
    await waitFor(() =>
      expect(screen.getByText(/sem dados/i)).toBeInTheDocument()
    );
  });
});

// ------------------------------------------------------------------ //
// T076 — DeliveryHistogram
// ------------------------------------------------------------------ //

describe("T076 — DeliveryHistogram", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("T076h: exibe skeleton de carregamento antes dos dados chegarem", () => {
    mockLoad.mockImplementation(() => new Promise(() => {}));
    render(<DeliveryHistogram />);
    expect(screen.getByTestId("delivery-histogram-loading")).toBeInTheDocument();
  });

  it("T076i: renderiza histograma após carregar dados", async () => {
    mockLoad.mockResolvedValue(temposFixture);
    render(<DeliveryHistogram />);
    await waitFor(() =>
      expect(screen.getByTestId("delivery-histogram")).toBeInTheDocument()
    );
  });

  it("T076j: exibe mensagem quando dados estão vazios", async () => {
    mockLoad.mockResolvedValue([]);
    render(<DeliveryHistogram />);
    await waitFor(() =>
      expect(screen.getByText(/sem dados/i)).toBeInTheDocument()
    );
  });

  it("T076k: chama loadChapterData com o arquivo de tempos", async () => {
    mockLoad.mockResolvedValue(temposFixture);
    render(<DeliveryHistogram />);
    await waitFor(() =>
      expect(mockLoad).toHaveBeenCalledWith("01_funil_tempos.json")
    );
  });
});
