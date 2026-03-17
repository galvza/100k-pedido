"""Testes das queries SQL — todos os 6 capítulos."""

from __future__ import annotations

import duckdb
import pandas as pd
import pytest

from pipeline.queries import run_query


# T011 — Query runner genérico
class TestRunQuery:
    def test_returns_dict_of_dataframes(
        self, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """T011: run_query retorna dict[str, DataFrame]."""
        results = run_query("01_funil.sql", con=sample_db)
        assert isinstance(results, dict)
        for name, df in results.items():
            assert isinstance(name, str)
            assert isinstance(df, pd.DataFrame)

    def test_funil_has_three_results(
        self, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Funil gera 3 resultados: funil_status, funil_conversao, funil_tempos."""
        results = run_query("01_funil.sql", con=sample_db)
        assert set(results.keys()) == {
            "funil_status",
            "funil_conversao",
            "funil_tempos",
        }

    def test_invalid_sql_file_raises(
        self, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Arquivo inexistente levanta FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            run_query("inexistente.sql", con=sample_db)


# T020 — Contagem por status
class TestFunilStatus:
    @pytest.fixture
    def df_status(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("01_funil.sql", con=sample_db)["funil_status"]

    def test_columns(self, df_status: pd.DataFrame) -> None:
        """T020: DataFrame de status tem colunas corretas."""
        assert list(df_status.columns) == ["status", "contagem", "percentual"]

    def test_sum_equals_total_orders(
        self, df_status: pd.DataFrame, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Soma das contagens por status = total de pedidos na tabela orders."""
        total_orders = sample_db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        assert df_status["contagem"].sum() == total_orders

    def test_percentages_sum_to_100(self, df_status: pd.DataFrame) -> None:
        """Percentuais somam ~100%."""
        total_pct = df_status["percentual"].sum()
        assert abs(total_pct - 100.0) < 1.0

    def test_delivered_is_majority(self, df_status: pd.DataFrame) -> None:
        """Status 'delivered' tem a maior contagem."""
        top_status = df_status.iloc[0]["status"]
        assert top_status == "delivered"


# T021 — Conversão entre etapas
class TestFunilConversao:
    @pytest.fixture
    def df_conversao(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("01_funil.sql", con=sample_db)["funil_conversao"]

    def test_columns(self, df_conversao: pd.DataFrame) -> None:
        """T021: DataFrame de conversão tem colunas corretas."""
        assert list(df_conversao.columns) == [
            "etapa",
            "pedidos",
            "taxa_conversao",
            "tempo_medio_dias",
        ]

    def test_four_stages(self, df_conversao: pd.DataFrame) -> None:
        """Funil tem 4 etapas na ordem correta."""
        etapas = list(df_conversao["etapa"])
        assert etapas == ["Compra", "Aprovacao", "Envio", "Entrega"]

    def test_first_stage_rate_is_one(self, df_conversao: pd.DataFrame) -> None:
        """Taxa de conversão da primeira etapa (Compra) é 1.0."""
        assert float(df_conversao.iloc[0]["taxa_conversao"]) == 1.0

    def test_conversion_rates_between_zero_and_one(
        self, df_conversao: pd.DataFrame
    ) -> None:
        """Todas as taxas de conversão estão entre 0 e 1."""
        for _, row in df_conversao.iterrows():
            rate = float(row["taxa_conversao"])
            assert 0.0 <= rate <= 1.0, f"Taxa fora do range: {rate} em {row['etapa']}"

    def test_pedidos_decrease_through_funnel(self, df_conversao: pd.DataFrame) -> None:
        """Contagem de pedidos diminui ou se mantém ao longo do funil."""
        pedidos = list(df_conversao["pedidos"])
        for i in range(1, len(pedidos)):
            assert (
                pedidos[i] <= pedidos[i - 1]
            ), f"Etapa {i} ({pedidos[i]}) > etapa {i-1} ({pedidos[i-1]})"

    def test_time_means_are_non_negative(self, df_conversao: pd.DataFrame) -> None:
        """Tempos médios são >= 0."""
        for _, row in df_conversao.iterrows():
            tempo = float(row["tempo_medio_dias"])
            assert tempo >= 0.0, f"Tempo negativo em {row['etapa']}: {tempo}"


# T022 — Distribuição de tempos de entrega
class TestFunilTempos:
    @pytest.fixture
    def df_tempos(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("01_funil.sql", con=sample_db)["funil_tempos"]

    def test_columns(self, df_tempos: pd.DataFrame) -> None:
        """T022: DataFrame de tempos tem colunas corretas."""
        expected_cols = [
            "faixa",
            "contagem",
            "media_dias_na_faixa",
            "min_dias",
            "max_dias",
        ]
        assert list(df_tempos.columns) == expected_cols

    def test_has_delivery_time_ranges(self, df_tempos: pd.DataFrame) -> None:
        """Pelo menos uma faixa de tempo presente."""
        assert len(df_tempos) > 0

    def test_counts_sum_to_delivered_orders(
        self, df_tempos: pd.DataFrame, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """T023: Soma das contagens = total de pedidos delivered."""
        delivered = sample_db.execute("""
            SELECT COUNT(*) FROM orders
            WHERE order_status = 'delivered'
              AND order_delivered_customer_date IS NOT NULL
        """).fetchone()[0]
        assert df_tempos["contagem"].sum() == delivered

    def test_ranges_ordered(self, df_tempos: pd.DataFrame) -> None:
        """Faixas estão ordenadas por min_dias."""
        min_dias = list(df_tempos["min_dias"])
        assert min_dias == sorted(min_dias)

    def test_averages_within_range(self, df_tempos: pd.DataFrame) -> None:
        """Média de dias na faixa está entre min e max."""
        for _, row in df_tempos.iterrows():
            avg = float(row["media_dias_na_faixa"])
            mn = float(row["min_dias"])
            mx = float(row["max_dias"])
            assert (
                mn <= avg <= mx
            ), f"Faixa {row['faixa']}: media {avg} fora de [{mn}, {mx}]"


# =========================================================
# Cap. 2 — RFM Segmentation
# =========================================================

VALID_SEGMENTS = {
    "Champions",
    "Loyal",
    "New Customers",
    "Promising",
    "At Risk",
    "Need Attention",
    "Lost",
    "Hibernating",
}


# T012 — Query RFM executa e retorna resultados corretos
class TestRfmQuery:
    def test_rfm_has_two_results(self, sample_db: duckdb.DuckDBPyConnection) -> None:
        """T012: RFM gera 2 resultados: rfm_scores e rfm_segmentos."""
        results = run_query("02_rfm.sql", con=sample_db)
        assert set(results.keys()) == {"rfm_scores", "rfm_segmentos"}


# T017 — Scores RFM por cliente
class TestRfmScores:
    @pytest.fixture
    def df_scores(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("02_rfm.sql", con=sample_db)["rfm_scores"]

    def test_columns(self, df_scores: pd.DataFrame) -> None:
        """DataFrame de scores tem todas as colunas esperadas."""
        expected = [
            "customer_unique_id",
            "recency",
            "frequency",
            "monetary",
            "r_score",
            "f_score",
            "m_score",
            "segmento",
        ]
        assert list(df_scores.columns) == expected

    def test_total_equals_distinct_delivered_customers(
        self, df_scores: pd.DataFrame, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """T017: Total de clientes = customer_unique_id distintos com pedido delivered."""
        expected = sample_db.execute("""
            SELECT COUNT(DISTINCT c.customer_unique_id)
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
        """).fetchone()[0]
        assert len(df_scores) == expected

    def test_no_duplicate_customers(self, df_scores: pd.DataFrame) -> None:
        """Cada customer_unique_id aparece exatamente 1 vez."""
        assert df_scores["customer_unique_id"].is_unique

    def test_scores_between_1_and_5(self, df_scores: pd.DataFrame) -> None:
        """Todos os scores (R, F, M) estão entre 1 e 5."""
        for col in ["r_score", "f_score", "m_score"]:
            assert df_scores[col].min() >= 1, f"{col} tem valor < 1"
            assert df_scores[col].max() <= 5, f"{col} tem valor > 5"

    def test_recency_is_positive(self, df_scores: pd.DataFrame) -> None:
        """Recency é positivo (dias desde última compra)."""
        assert (df_scores["recency"] > 0).all()

    def test_frequency_is_positive(self, df_scores: pd.DataFrame) -> None:
        """Frequency é >= 1 (pelo menos 1 pedido delivered)."""
        assert (df_scores["frequency"] >= 1).all()

    def test_monetary_is_positive(self, df_scores: pd.DataFrame) -> None:
        """Monetary é positivo."""
        assert (df_scores["monetary"] > 0).all()

    def test_every_customer_has_valid_segment(self, df_scores: pd.DataFrame) -> None:
        """Todo cliente pertence a um segmento válido."""
        segments_found = set(df_scores["segmento"].unique())
        assert segments_found.issubset(
            VALID_SEGMENTS
        ), f"Segmentos inesperados: {segments_found - VALID_SEGMENTS}"

    def test_higher_r_score_means_lower_recency(self, df_scores: pd.DataFrame) -> None:
        """Clientes com r_score=5 têm recency menor que r_score=1."""
        r5 = df_scores[df_scores["r_score"] == 5]["recency"].mean()
        r1 = df_scores[df_scores["r_score"] == 1]["recency"].mean()
        assert r5 < r1, f"r_score=5 recency ({r5}) >= r_score=1 ({r1})"


# T024 — Perfil agregado por segmento
class TestRfmSegmentos:
    @pytest.fixture
    def df_segmentos(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("02_rfm.sql", con=sample_db)["rfm_segmentos"]

    @pytest.fixture
    def df_scores(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("02_rfm.sql", con=sample_db)["rfm_scores"]

    def test_columns(self, df_segmentos: pd.DataFrame) -> None:
        """T024: DataFrame de segmentos tem colunas corretas."""
        expected = [
            "segmento",
            "contagem",
            "percentual",
            "recencia_media",
            "frequencia_media",
            "monetario_medio",
            "r_score_medio",
            "f_score_medio",
            "m_score_medio",
        ]
        assert list(df_segmentos.columns) == expected

    def test_all_segments_valid(self, df_segmentos: pd.DataFrame) -> None:
        """Todos os segmentos são da lista definida."""
        segments_found = set(df_segmentos["segmento"])
        assert segments_found.issubset(VALID_SEGMENTS)

    def test_sum_equals_total_customers(
        self, df_segmentos: pd.DataFrame, df_scores: pd.DataFrame
    ) -> None:
        """Soma das contagens por segmento = total de clientes."""
        assert df_segmentos["contagem"].sum() == len(df_scores)

    def test_percentages_sum_to_100(self, df_segmentos: pd.DataFrame) -> None:
        """Percentuais somam ~100%."""
        total = float(df_segmentos["percentual"].sum())
        assert abs(total - 100.0) < 1.0

    def test_no_duplicate_segments(self, df_segmentos: pd.DataFrame) -> None:
        """Cada segmento aparece exatamente 1 vez."""
        assert df_segmentos["segmento"].is_unique

    def test_champions_have_high_scores(self, df_segmentos: pd.DataFrame) -> None:
        """Champions têm scores médios altos."""
        champs = df_segmentos[df_segmentos["segmento"] == "Champions"]
        if len(champs) > 0:
            row = champs.iloc[0]
            assert float(row["r_score_medio"]) >= 4.0
            assert float(row["f_score_medio"]) >= 4.0
            assert float(row["m_score_medio"]) >= 4.0


# =========================================================
# Cap. 3 — Cohort Analysis
# =========================================================


# T013 — Query Cohort executa e retorna resultados corretos
class TestCohortQuery:
    def test_cohort_has_two_results(self, sample_db: duckdb.DuckDBPyConnection) -> None:
        """T013: Cohort gera 2 resultados: cohort_retencao e cohort_recompra."""
        results = run_query("03_cohort.sql", con=sample_db)
        assert set(results.keys()) == {"cohort_retencao", "cohort_recompra"}


# T018 — Matriz de retenção
class TestCohortRetencao:
    @pytest.fixture
    def df_retencao(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("03_cohort.sql", con=sample_db)["cohort_retencao"]

    def test_columns(self, df_retencao: pd.DataFrame) -> None:
        """T018: DataFrame de retenção tem colunas corretas."""
        expected = [
            "coorte_mes",
            "periodo",
            "clientes_ativos",
            "tamanho_coorte",
            "taxa_retencao",
        ]
        assert list(df_retencao.columns) == expected

    def test_period_zero_rate_is_one(self, df_retencao: pd.DataFrame) -> None:
        """Período 0 de cada coorte tem taxa_retencao = 1.0."""
        p0 = df_retencao[df_retencao["periodo"] == 0]
        assert len(p0) > 0, "Nenhum período 0 encontrado"
        for _, row in p0.iterrows():
            assert (
                float(row["taxa_retencao"]) == 1.0
            ), f"Coorte {row['coorte_mes']}: taxa periodo 0 = {row['taxa_retencao']}"

    def test_retention_between_zero_and_one(self, df_retencao: pd.DataFrame) -> None:
        """Todas as taxas de retenção estão entre 0.0 e 1.0."""
        for _, row in df_retencao.iterrows():
            rate = float(row["taxa_retencao"])
            assert (
                0.0 <= rate <= 1.0
            ), f"Taxa fora do range: {rate} em coorte {row['coorte_mes']} p{row['periodo']}"

    def test_periods_are_non_negative(self, df_retencao: pd.DataFrame) -> None:
        """Todos os períodos são >= 0."""
        assert (df_retencao["periodo"] >= 0).all()

    def test_cohort_dates_not_after_dataset_end(
        self, df_retencao: pd.DataFrame
    ) -> None:
        """Nenhuma coorte posterior a outubro 2018."""
        max_coorte = pd.Timestamp(df_retencao["coorte_mes"].max())
        assert max_coorte <= pd.Timestamp("2018-10-01")

    def test_every_cohort_has_period_zero(self, df_retencao: pd.DataFrame) -> None:
        """Toda coorte presente tem pelo menos o período 0."""
        coortes = set(df_retencao["coorte_mes"].unique())
        p0_coortes = set(
            df_retencao[df_retencao["periodo"] == 0]["coorte_mes"].unique()
        )
        assert coortes == p0_coortes

    def test_clientes_ativos_lte_tamanho_coorte(
        self, df_retencao: pd.DataFrame
    ) -> None:
        """Clientes ativos nunca excedem o tamanho da coorte."""
        for _, row in df_retencao.iterrows():
            assert row["clientes_ativos"] <= row["tamanho_coorte"], (
                f"Coorte {row['coorte_mes']} p{row['periodo']}: "
                f"ativos ({row['clientes_ativos']}) > tamanho ({row['tamanho_coorte']})"
            )

    def test_ordered_by_cohort_then_period(self, df_retencao: pd.DataFrame) -> None:
        """Resultado está ordenado por coorte, depois por período."""
        coortes = list(df_retencao["coorte_mes"])
        periodos = list(df_retencao["periodo"])
        pairs = list(zip(coortes, periodos))
        assert pairs == sorted(pairs)


# T025 — Métricas de recompra
class TestCohortRecompra:
    @pytest.fixture
    def df_recompra(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("03_cohort.sql", con=sample_db)["cohort_recompra"]

    def test_columns(self, df_recompra: pd.DataFrame) -> None:
        """T025: DataFrame de recompra tem colunas corretas."""
        expected = [
            "total_clientes",
            "clientes_recompra",
            "taxa_recompra_pct",
            "media_pedidos_por_cliente",
            "dias_medio_ate_recompra",
        ]
        assert list(df_recompra.columns) == expected

    def test_single_row(self, df_recompra: pd.DataFrame) -> None:
        """Resultado de recompra é uma única linha agregada."""
        assert len(df_recompra) == 1

    def test_recompra_lte_total(self, df_recompra: pd.DataFrame) -> None:
        """Clientes com recompra <= total de clientes."""
        row = df_recompra.iloc[0]
        assert row["clientes_recompra"] <= row["total_clientes"]

    def test_taxa_between_zero_and_100(self, df_recompra: pd.DataFrame) -> None:
        """Taxa de recompra entre 0% e 100%."""
        taxa = float(df_recompra.iloc[0]["taxa_recompra_pct"])
        assert 0.0 <= taxa <= 100.0

    def test_media_pedidos_gte_one(self, df_recompra: pd.DataFrame) -> None:
        """Média de pedidos por cliente >= 1.0."""
        media = float(df_recompra.iloc[0]["media_pedidos_por_cliente"])
        assert media >= 1.0

    def test_dias_recompra_positive(self, df_recompra: pd.DataFrame) -> None:
        """Dias médio até recompra é positivo (se há recompra)."""
        row = df_recompra.iloc[0]
        if row["clientes_recompra"] > 0:
            assert float(row["dias_medio_ate_recompra"]) > 0


# =========================================================
# Cap. 4 — Análise Geográfica
# =========================================================

VALID_UFS = {
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
}


# T014 — Query Geo executa e retorna resultados corretos
class TestGeoQuery:
    def test_geo_has_two_results(self, sample_db: duckdb.DuckDBPyConnection) -> None:
        """T014: Geo gera 2 resultados: geo_estados e geo_categorias."""
        results = run_query("04_geo.sql", con=sample_db)
        assert set(results.keys()) == {"geo_estados", "geo_categorias"}


# T019 — Métricas por estado
class TestGeoEstados:
    @pytest.fixture
    def df_estados(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("04_geo.sql", con=sample_db)["geo_estados"]

    def test_columns(self, df_estados: pd.DataFrame) -> None:
        """T019: DataFrame de estados tem colunas corretas."""
        expected = [
            "estado",
            "pedidos",
            "receita",
            "ticket_medio",
            "frete_medio",
            "frete_percentual",
            "review_score_medio",
            "total_vendedores",
        ]
        assert list(df_estados.columns) == expected

    def test_states_are_valid_ufs(self, df_estados: pd.DataFrame) -> None:
        """Todos os estados são UFs brasileiras válidas."""
        states = set(df_estados["estado"])
        assert states.issubset(VALID_UFS), f"UFs invalidas: {states - VALID_UFS}"

    def test_at_most_27_rows(self, df_estados: pd.DataFrame) -> None:
        """No máximo 27 linhas (uma por UF)."""
        assert len(df_estados) <= 27

    def test_no_duplicate_states(self, df_estados: pd.DataFrame) -> None:
        """Cada UF aparece no máximo 1 vez."""
        assert df_estados["estado"].is_unique

    def test_pedidos_positive(self, df_estados: pd.DataFrame) -> None:
        """Todos os estados têm pelo menos 1 pedido."""
        assert (df_estados["pedidos"] > 0).all()

    def test_receita_positive(self, df_estados: pd.DataFrame) -> None:
        """Receita é positiva em todos os estados."""
        assert (df_estados["receita"] > 0).all()

    def test_ticket_medio_positive(self, df_estados: pd.DataFrame) -> None:
        """Ticket médio é positivo."""
        assert (df_estados["ticket_medio"] > 0).all()

    def test_frete_medio_positive(self, df_estados: pd.DataFrame) -> None:
        """Frete médio é positivo."""
        assert (df_estados["frete_medio"] > 0).all()

    def test_frete_percentual_between_zero_and_one(
        self, df_estados: pd.DataFrame
    ) -> None:
        """Frete percentual está entre 0 e 1."""
        assert (df_estados["frete_percentual"] >= 0).all()
        assert (df_estados["frete_percentual"] <= 1).all()

    def test_review_score_between_1_and_5(self, df_estados: pd.DataFrame) -> None:
        """Review score médio está entre 1.0 e 5.0."""
        assert (df_estados["review_score_medio"] >= 1.0).all()
        assert (df_estados["review_score_medio"] <= 5.0).all()

    def test_vendedores_non_negative(self, df_estados: pd.DataFrame) -> None:
        """Total de vendedores é >= 0 (pode ser 0 em estados sem vendedores)."""
        assert (df_estados["total_vendedores"] >= 0).all()

    def test_ordered_by_pedidos_desc(self, df_estados: pd.DataFrame) -> None:
        """Estados ordenados por número de pedidos decrescente."""
        pedidos = list(df_estados["pedidos"])
        assert pedidos == sorted(pedidos, reverse=True)

    def test_sum_pedidos_matches_delivered(
        self, df_estados: pd.DataFrame, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Soma de pedidos por estado = total de pedidos delivered."""
        total_delivered = sample_db.execute("""
            SELECT COUNT(DISTINCT o.order_id)
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
        """).fetchone()[0]
        assert df_estados["pedidos"].sum() == total_delivered


# T019 — Top categorias por estado
class TestGeoCategorias:
    @pytest.fixture
    def df_categorias(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("04_geo.sql", con=sample_db)["geo_categorias"]

    def test_columns(self, df_categorias: pd.DataFrame) -> None:
        """DataFrame de categorias tem colunas corretas."""
        expected = ["estado", "categoria", "pedidos", "receita"]
        assert list(df_categorias.columns) == expected

    def test_max_3_per_state(self, df_categorias: pd.DataFrame) -> None:
        """Cada estado tem no máximo 3 categorias."""
        counts = df_categorias.groupby("estado").size()
        assert (counts <= 3).all()

    def test_states_are_valid_ufs(self, df_categorias: pd.DataFrame) -> None:
        """Todos os estados são UFs válidas."""
        states = set(df_categorias["estado"])
        assert states.issubset(VALID_UFS)

    def test_pedidos_positive(self, df_categorias: pd.DataFrame) -> None:
        """Contagem de pedidos é positiva."""
        assert (df_categorias["pedidos"] > 0).all()

    def test_receita_positive(self, df_categorias: pd.DataFrame) -> None:
        """Receita por categoria é positiva."""
        assert (df_categorias["receita"] > 0).all()


# =========================================================
# Cap. 5 — Sazonalidade
# =========================================================


# T015 — Query Sazonalidade executa e retorna resultados corretos
class TestSazonalidadeQuery:
    def test_has_three_results(self, sample_db: duckdb.DuckDBPyConnection) -> None:
        """T015: Sazonalidade gera 3 resultados nomeados."""
        results = run_query("05_sazonalidade.sql", con=sample_db)
        assert set(results.keys()) == {
            "sazonalidade_mensal",
            "sazonalidade_semanal",
            "sazonalidade_horaria",
        }


class TestSazonalidadeMensal:
    @pytest.fixture
    def df_mensal(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("05_sazonalidade.sql", con=sample_db)["sazonalidade_mensal"]

    def test_columns(self, df_mensal: pd.DataFrame) -> None:
        """DataFrame mensal tem colunas corretas."""
        expected = ["mes", "pedidos", "receita", "media_movel_3m", "mom_growth"]
        assert list(df_mensal.columns) == expected

    def test_ordered_by_month(self, df_mensal: pd.DataFrame) -> None:
        """Meses estão em ordem crescente."""
        meses = list(df_mensal["mes"])
        assert meses == sorted(meses)

    def test_pedidos_positive(self, df_mensal: pd.DataFrame) -> None:
        """Todos os meses têm pelo menos 1 pedido."""
        assert (df_mensal["pedidos"] > 0).all()

    def test_receita_positive(self, df_mensal: pd.DataFrame) -> None:
        """Receita é positiva em todos os meses."""
        assert (df_mensal["receita"] > 0).all()

    def test_media_movel_null_first_two_months(self, df_mensal: pd.DataFrame) -> None:
        """Média móvel é NULL/NaN nos 2 primeiros meses."""
        assert pd.isna(df_mensal.iloc[0]["media_movel_3m"])
        assert pd.isna(df_mensal.iloc[1]["media_movel_3m"])

    def test_media_movel_not_null_from_third_month(
        self, df_mensal: pd.DataFrame
    ) -> None:
        """Média móvel é preenchida a partir do 3o mês."""
        if len(df_mensal) >= 3:
            assert pd.notna(df_mensal.iloc[2]["media_movel_3m"])

    def test_media_movel_positive_when_present(self, df_mensal: pd.DataFrame) -> None:
        """Média móvel é positiva quando presente."""
        valid = df_mensal["media_movel_3m"].dropna()
        assert (valid > 0).all()

    def test_mom_growth_null_first_month(self, df_mensal: pd.DataFrame) -> None:
        """MoM growth é NULL no primeiro mês."""
        assert pd.isna(df_mensal.iloc[0]["mom_growth"])

    def test_mom_growth_not_null_from_second(self, df_mensal: pd.DataFrame) -> None:
        """MoM growth é preenchido a partir do 2o mês."""
        if len(df_mensal) >= 2:
            assert pd.notna(df_mensal.iloc[1]["mom_growth"])


class TestSazonalidadeSemanal:
    @pytest.fixture
    def df_semanal(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("05_sazonalidade.sql", con=sample_db)["sazonalidade_semanal"]

    def test_columns(self, df_semanal: pd.DataFrame) -> None:
        """DataFrame semanal tem colunas corretas."""
        expected = ["dia_semana", "pedidos_medio", "receita_media", "ticket_medio"]
        assert list(df_semanal.columns) == expected

    def test_seven_days(self, df_semanal: pd.DataFrame) -> None:
        """Exatamente 7 dias da semana (0-6)."""
        assert len(df_semanal) == 7
        assert set(df_semanal["dia_semana"]) == {0, 1, 2, 3, 4, 5, 6}

    def test_ordered_by_day(self, df_semanal: pd.DataFrame) -> None:
        """Dias ordenados de 0 a 6."""
        dias = list(df_semanal["dia_semana"])
        assert dias == list(range(7))

    def test_pedidos_medio_positive(self, df_semanal: pd.DataFrame) -> None:
        """Pedidos médio é positivo."""
        assert (df_semanal["pedidos_medio"] > 0).all()

    def test_receita_media_positive(self, df_semanal: pd.DataFrame) -> None:
        """Receita média é positiva."""
        assert (df_semanal["receita_media"] > 0).all()

    def test_ticket_medio_positive(self, df_semanal: pd.DataFrame) -> None:
        """Ticket médio é positivo."""
        assert (df_semanal["ticket_medio"] > 0).all()


class TestSazonalidadeHoraria:
    @pytest.fixture
    def df_horaria(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("05_sazonalidade.sql", con=sample_db)["sazonalidade_horaria"]

    def test_columns(self, df_horaria: pd.DataFrame) -> None:
        """DataFrame horária tem colunas corretas."""
        expected = ["hora", "pedidos", "receita"]
        assert list(df_horaria.columns) == expected

    def test_hours_between_0_and_23(self, df_horaria: pd.DataFrame) -> None:
        """Horas estão entre 0 e 23."""
        assert df_horaria["hora"].min() >= 0
        assert df_horaria["hora"].max() <= 23

    def test_ordered_by_hour(self, df_horaria: pd.DataFrame) -> None:
        """Horas ordenadas crescente."""
        horas = list(df_horaria["hora"])
        assert horas == sorted(horas)

    def test_pedidos_positive(self, df_horaria: pd.DataFrame) -> None:
        """Pedidos por hora são positivos."""
        assert (df_horaria["pedidos"] > 0).all()

    def test_receita_positive(self, df_horaria: pd.DataFrame) -> None:
        """Receita por hora é positiva."""
        assert (df_horaria["receita"] > 0).all()

    def test_no_duplicate_hours(self, df_horaria: pd.DataFrame) -> None:
        """Cada hora aparece no máximo 1 vez."""
        assert df_horaria["hora"].is_unique


# =========================================================
# Cap. 6 — Reviews e Satisfação
# =========================================================


# T016 — Query Reviews executa e retorna resultados corretos
class TestReviewsQuery:
    def test_has_five_results(self, sample_db: duckdb.DuckDBPyConnection) -> None:
        """T016: Reviews gera 5 resultados nomeados."""
        results = run_query("06_reviews.sql", con=sample_db)
        assert set(results.keys()) == {
            "reviews_distribuicao",
            "reviews_nps",
            "reviews_categorias",
            "reviews_atraso",
            "reviews_comentarios",
        }


class TestReviewsDistribuicao:
    @pytest.fixture
    def df_dist(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("06_reviews.sql", con=sample_db)["reviews_distribuicao"]

    def test_columns(self, df_dist: pd.DataFrame) -> None:
        """DataFrame distribuição tem colunas corretas."""
        assert list(df_dist.columns) == ["score", "contagem", "percentual"]

    def test_five_scores(self, df_dist: pd.DataFrame) -> None:
        """Exatamente 5 scores (1-5)."""
        assert len(df_dist) == 5
        assert list(df_dist["score"]) == [1, 2, 3, 4, 5]

    def test_percentages_sum_to_100(self, df_dist: pd.DataFrame) -> None:
        """Percentuais somam ~100%."""
        total = float(df_dist["percentual"].sum())
        assert abs(total - 100.0) < 1.0

    def test_contagem_matches_total_reviews(
        self, df_dist: pd.DataFrame, sample_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Soma das contagens = total de reviews."""
        total = sample_db.execute("SELECT COUNT(*) FROM order_reviews").fetchone()[0]
        assert df_dist["contagem"].sum() == total


class TestReviewsNps:
    @pytest.fixture
    def df_nps(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("06_reviews.sql", con=sample_db)["reviews_nps"]

    def test_columns(self, df_nps: pd.DataFrame) -> None:
        """DataFrame NPS tem colunas corretas."""
        expected = [
            "promotores",
            "neutros",
            "detratores",
            "total",
            "pct_promotores",
            "pct_detratores",
            "nps",
        ]
        assert list(df_nps.columns) == expected

    def test_single_row(self, df_nps: pd.DataFrame) -> None:
        """NPS é uma única linha agregada."""
        assert len(df_nps) == 1

    def test_nps_between_minus_100_and_100(self, df_nps: pd.DataFrame) -> None:
        """NPS está entre -100 e 100."""
        nps = float(df_nps.iloc[0]["nps"])
        assert -100.0 <= nps <= 100.0

    def test_parts_sum_to_total(self, df_nps: pd.DataFrame) -> None:
        """Promotores + neutros + detratores = total."""
        row = df_nps.iloc[0]
        assert row["promotores"] + row["neutros"] + row["detratores"] == row["total"]

    def test_nps_equals_pct_diff(self, df_nps: pd.DataFrame) -> None:
        """NPS = pct_promotores - pct_detratores."""
        row = df_nps.iloc[0]
        expected_nps = float(row["pct_promotores"]) - float(row["pct_detratores"])
        assert abs(float(row["nps"]) - expected_nps) < 0.1


class TestReviewsCategorias:
    @pytest.fixture
    def df_cat(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("06_reviews.sql", con=sample_db)["reviews_categorias"]

    def test_columns(self, df_cat: pd.DataFrame) -> None:
        """DataFrame categorias tem colunas corretas."""
        expected = [
            "categoria",
            "total_reviews",
            "score_medio",
            "reviews_positivas",
            "reviews_negativas",
        ]
        assert list(df_cat.columns) == expected

    def test_score_medio_between_1_and_5(self, df_cat: pd.DataFrame) -> None:
        """Score médio de cada categoria está entre 1.0 e 5.0."""
        assert (df_cat["score_medio"] >= 1.0).all()
        assert (df_cat["score_medio"] <= 5.0).all()

    def test_ordered_by_score_desc(self, df_cat: pd.DataFrame) -> None:
        """Categorias ordenadas por score decrescente."""
        scores = list(df_cat["score_medio"])
        assert scores == sorted(scores, reverse=True)

    def test_min_reviews_threshold(self, df_cat: pd.DataFrame) -> None:
        """Todas as categorias têm >= 2 reviews (HAVING)."""
        assert (df_cat["total_reviews"] >= 2).all()

    def test_no_duplicate_categories(self, df_cat: pd.DataFrame) -> None:
        """Cada categoria aparece 1 vez."""
        assert df_cat["categoria"].is_unique


class TestReviewsAtraso:
    @pytest.fixture
    def df_atraso(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("06_reviews.sql", con=sample_db)["reviews_atraso"]

    def test_columns(self, df_atraso: pd.DataFrame) -> None:
        """DataFrame atraso tem colunas corretas."""
        expected = ["faixa_atraso", "contagem", "score_medio", "min_dias", "max_dias"]
        assert list(df_atraso.columns) == expected

    def test_score_medio_between_1_and_5(self, df_atraso: pd.DataFrame) -> None:
        """Score médio em cada faixa está entre 1.0 e 5.0."""
        assert (df_atraso["score_medio"] >= 1.0).all()
        assert (df_atraso["score_medio"] <= 5.0).all()

    def test_ordered_by_min_dias(self, df_atraso: pd.DataFrame) -> None:
        """Faixas ordenadas por min_dias."""
        min_dias = list(df_atraso["min_dias"])
        assert min_dias == sorted(min_dias)

    def test_negative_dias_allowed(self, df_atraso: pd.DataFrame) -> None:
        """Dias negativos são permitidos (entrega antecipada)."""
        assert df_atraso["min_dias"].min() < 0

    def test_contagem_positive(self, df_atraso: pd.DataFrame) -> None:
        """Todas as faixas têm contagem > 0."""
        assert (df_atraso["contagem"] > 0).all()


class TestReviewsComentarios:
    @pytest.fixture
    def df_com(self, sample_db: duckdb.DuckDBPyConnection) -> pd.DataFrame:
        return run_query("06_reviews.sql", con=sample_db)["reviews_comentarios"]

    def test_columns(self, df_com: pd.DataFrame) -> None:
        """DataFrame comentários tem colunas corretas."""
        expected = ["com_comentario", "sem_comentario", "total", "pct_com_comentario"]
        assert list(df_com.columns) == expected

    def test_single_row(self, df_com: pd.DataFrame) -> None:
        """Resultado é uma única linha."""
        assert len(df_com) == 1

    def test_parts_sum_to_total(self, df_com: pd.DataFrame) -> None:
        """com_comentario + sem_comentario = total."""
        row = df_com.iloc[0]
        assert row["com_comentario"] + row["sem_comentario"] == row["total"]

    def test_pct_between_0_and_100(self, df_com: pd.DataFrame) -> None:
        """Percentual com comentário entre 0 e 100."""
        pct = float(df_com.iloc[0]["pct_com_comentario"])
        assert 0.0 <= pct <= 100.0
