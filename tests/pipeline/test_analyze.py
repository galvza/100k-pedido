"""Testes das análises Python — hipóteses (T033-T037), clustering (T038-T043) e predição (T044-T050)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.analyze.hipoteses import (
    mann_whitney_test,
    resultado_formatado,
    t_test_independente,
)

# =========================================================
# Fixtures de dados para testes estatísticos
# =========================================================


@pytest.fixture
def grupos_diferentes() -> tuple[pd.Series, pd.Series]:
    """Dois grupos com distribuições claramente diferentes."""
    np.random.seed(42)
    a = pd.Series(np.random.normal(loc=10, scale=2, size=100))
    b = pd.Series(np.random.normal(loc=15, scale=2, size=100))
    return a, b


@pytest.fixture
def grupos_iguais() -> tuple[pd.Series, pd.Series]:
    """Dois grupos da mesma distribuição."""
    np.random.seed(42)
    a = pd.Series(np.random.normal(loc=10, scale=2, size=100))
    b = pd.Series(np.random.normal(loc=10, scale=2, size=100))
    return a, b


@pytest.fixture
def grupo_pequeno() -> pd.Series:
    """Grupo com apenas 1 observação."""
    return pd.Series([5.0])


@pytest.fixture
def grupo_com_nans() -> pd.Series:
    """Grupo com valores NaN."""
    return pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, np.nan, 7.0])


@pytest.fixture
def grupos_identicos() -> tuple[pd.Series, pd.Series]:
    """Dois grupos com valores exatamente iguais."""
    vals = pd.Series([3.0, 3.0, 3.0, 3.0, 3.0])
    return vals.copy(), vals.copy()


# =========================================================
# T033 — Mann-Whitney U test
# =========================================================


class TestMannWhitney:
    def test_returns_required_keys(self, grupos_diferentes: tuple) -> None:
        """T033: Resultado contém todas as chaves esperadas."""
        a, b = grupos_diferentes
        result = mann_whitney_test(a, b)
        expected_keys = {
            "teste_usado",
            "u_statistic",
            "p_value",
            "significativo",
            "tamanho_efeito",
            "n_a",
            "n_b",
            "alpha",
            "mensagem",
        }
        assert set(result.keys()) == expected_keys

    def test_p_value_between_0_and_1(self, grupos_diferentes: tuple) -> None:
        """p_value está entre 0 e 1."""
        a, b = grupos_diferentes
        result = mann_whitney_test(a, b)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_detects_significant_difference(self, grupos_diferentes: tuple) -> None:
        """Detecta diferença significativa entre grupos distintos."""
        a, b = grupos_diferentes
        result = mann_whitney_test(a, b)
        assert result["significativo"] is True
        assert result["p_value"] < 0.05

    def test_no_significance_for_same_distribution(self, grupos_iguais: tuple) -> None:
        """Não detecta diferença significativa para mesma distribuição."""
        a, b = grupos_iguais
        result = mann_whitney_test(a, b)
        assert result["significativo"] is False

    def test_insufficient_sample(
        self, grupo_pequeno: pd.Series, grupos_diferentes: tuple
    ) -> None:
        """Grupo com n=1 retorna inconclusivo."""
        _, b = grupos_diferentes
        result = mann_whitney_test(grupo_pequeno, b)
        assert result["significativo"] is None
        assert result["mensagem"] == "Amostra insuficiente"
        assert result["u_statistic"] is None

    def test_handles_nans(self, grupo_com_nans: pd.Series) -> None:
        """NaN são removidos antes do teste."""
        b = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
        result = mann_whitney_test(grupo_com_nans, b)
        assert result["n_a"] == 5  # 7 - 2 NaN
        assert result["p_value"] is not None

    def test_identical_groups(self, grupos_identicos: tuple) -> None:
        """Grupos idênticos: p ≈ 1.0, não significativo."""
        a, b = grupos_identicos
        result = mann_whitney_test(a, b)
        assert result["significativo"] is False
        assert result["p_value"] >= 0.9

    def test_custom_alpha(self, grupos_diferentes: tuple) -> None:
        """Alpha customizado é respeitado."""
        a, b = grupos_diferentes
        result = mann_whitney_test(a, b, alpha=0.001)
        assert result["alpha"] == 0.001

    def test_effect_size_range(self, grupos_diferentes: tuple) -> None:
        """Tamanho de efeito está entre -1 e 1."""
        a, b = grupos_diferentes
        result = mann_whitney_test(a, b)
        assert -1.0 <= result["tamanho_efeito"] <= 1.0

    def test_teste_usado(self, grupos_diferentes: tuple) -> None:
        """Campo teste_usado é 'Mann-Whitney U'."""
        a, b = grupos_diferentes
        result = mann_whitney_test(a, b)
        assert result["teste_usado"] == "Mann-Whitney U"


# =========================================================
# T034 — t-test independente
# =========================================================


class TestTTest:
    def test_returns_required_keys(self, grupos_diferentes: tuple) -> None:
        """T034: Resultado contém todas as chaves esperadas."""
        a, b = grupos_diferentes
        result = t_test_independente(a, b)
        expected_keys = {
            "teste_usado",
            "t_statistic",
            "p_value",
            "significativo",
            "cohens_d",
            "n_a",
            "n_b",
            "alpha",
            "mensagem",
        }
        assert set(result.keys()) == expected_keys

    def test_p_value_between_0_and_1(self, grupos_diferentes: tuple) -> None:
        """p_value está entre 0 e 1."""
        a, b = grupos_diferentes
        result = t_test_independente(a, b)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_detects_significant_difference(self, grupos_diferentes: tuple) -> None:
        """Detecta diferença significativa entre grupos distintos."""
        a, b = grupos_diferentes
        result = t_test_independente(a, b)
        assert result["significativo"] is True

    def test_no_significance_for_same_distribution(self, grupos_iguais: tuple) -> None:
        """Não detecta diferença para mesma distribuição."""
        a, b = grupos_iguais
        result = t_test_independente(a, b)
        assert result["significativo"] is False

    def test_insufficient_sample(
        self, grupo_pequeno: pd.Series, grupos_diferentes: tuple
    ) -> None:
        """Grupo com n=1 retorna inconclusivo."""
        _, b = grupos_diferentes
        result = t_test_independente(grupo_pequeno, b)
        assert result["significativo"] is None
        assert result["mensagem"] == "Amostra insuficiente"
        assert result["cohens_d"] is None

    def test_cohens_d_large_for_different_groups(
        self, grupos_diferentes: tuple
    ) -> None:
        """Cohen's d > 0.8 para grupos claramente diferentes."""
        a, b = grupos_diferentes
        result = t_test_independente(a, b)
        assert abs(result["cohens_d"]) > 0.8

    def test_cohens_d_small_for_same_distribution(self, grupos_iguais: tuple) -> None:
        """Cohen's d pequeno para mesma distribuição."""
        a, b = grupos_iguais
        result = t_test_independente(a, b)
        assert abs(result["cohens_d"]) < 0.5

    def test_handles_nans(self, grupo_com_nans: pd.Series) -> None:
        """NaN são removidos antes do teste."""
        b = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
        result = t_test_independente(grupo_com_nans, b)
        assert result["n_a"] == 5
        assert result["p_value"] is not None

    def test_identical_groups(self, grupos_identicos: tuple) -> None:
        """Grupos idênticos: p ≈ 1.0, não significativo."""
        a, b = grupos_identicos
        result = t_test_independente(a, b)
        assert result["significativo"] is False
        # p_value may be NaN for zero-variance groups, which is acceptable
        if result["p_value"] is not None and not np.isnan(result["p_value"]):
            assert result["p_value"] >= 0.9

    def test_teste_usado(self, grupos_diferentes: tuple) -> None:
        """Campo teste_usado é 'Welch t-test'."""
        a, b = grupos_diferentes
        result = t_test_independente(a, b)
        assert result["teste_usado"] == "Welch t-test"


# =========================================================
# T035-T037 — resultado_formatado
# =========================================================


class TestResultadoFormatado:
    def test_adds_hipotese(self, grupos_diferentes: tuple) -> None:
        """T035: resultado_formatado inclui a hipótese testada."""
        a, b = grupos_diferentes
        teste = mann_whitney_test(a, b)
        result = resultado_formatado(teste, "Frete alto reduz review score")
        assert result["hipotese"] == "Frete alto reduz review score"

    def test_adds_conclusao_significant(self, grupos_diferentes: tuple) -> None:
        """T036: Conclusão para resultado significativo."""
        a, b = grupos_diferentes
        teste = mann_whitney_test(a, b)
        result = resultado_formatado(teste, "H1")
        assert "Rejeita H0" in result["conclusao"]
        assert "significativa" in result["conclusao"]

    def test_adds_conclusao_not_significant(self, grupos_iguais: tuple) -> None:
        """Conclusão para resultado não significativo."""
        a, b = grupos_iguais
        teste = mann_whitney_test(a, b)
        result = resultado_formatado(teste, "H1")
        assert "Nao rejeita H0" in result["conclusao"]

    def test_adds_premissas(self, grupos_diferentes: tuple) -> None:
        """Resultado inclui premissas do teste."""
        a, b = grupos_diferentes
        teste = mann_whitney_test(a, b)
        result = resultado_formatado(teste, "H1")
        assert "premissas" in result
        assert "nao-parametrico" in result["premissas"]
        assert "n=" in result["premissas"]

    def test_premissas_ttest(self, grupos_diferentes: tuple) -> None:
        """Premissas do t-test mencionam Welch."""
        a, b = grupos_diferentes
        teste = t_test_independente(a, b)
        result = resultado_formatado(teste, "H1")
        assert "Welch" in result["premissas"]

    def test_insufficient_sample_conclusion(
        self, grupo_pequeno: pd.Series, grupos_diferentes: tuple
    ) -> None:
        """T037: Amostra insuficiente gera conclusão de inconclusivo."""
        _, b = grupos_diferentes
        teste = mann_whitney_test(grupo_pequeno, b)
        result = resultado_formatado(teste, "H1")
        assert "Inconclusivo" in result["conclusao"]
        assert "insuficiente" in result["conclusao"]

    def test_includes_effect_size_label(self, grupos_diferentes: tuple) -> None:
        """Conclusão inclui label do tamanho de efeito."""
        a, b = grupos_diferentes
        teste = mann_whitney_test(a, b)
        result = resultado_formatado(teste, "H1")
        assert any(
            label in result["conclusao"]
            for label in ["negligivel", "pequeno", "medio", "grande"]
        )

    def test_includes_cohens_d_label(self, grupos_diferentes: tuple) -> None:
        """Conclusão do t-test inclui Cohen's d."""
        a, b = grupos_diferentes
        teste = t_test_independente(a, b)
        result = resultado_formatado(teste, "H1")
        assert "Cohen's d" in result["conclusao"]

    def test_preserves_original_keys(self, grupos_diferentes: tuple) -> None:
        """resultado_formatado preserva todas as chaves do teste original."""
        a, b = grupos_diferentes
        teste = mann_whitney_test(a, b)
        result = resultado_formatado(teste, "H1")
        for key in teste:
            assert key in result

    def test_includes_alpha_in_premissas(self, grupos_diferentes: tuple) -> None:
        """Premissas mencionam nível de significância."""
        a, b = grupos_diferentes
        teste = mann_whitney_test(a, b, alpha=0.01)
        result = resultado_formatado(teste, "H1")
        assert "0.01" in result["premissas"]


# =========================================================
# Clustering fixtures
# =========================================================

from pipeline.analyze.clustering import (
    elbow_method,
    normalizar_features,
    pipeline_clustering,
    rodar_kmeans,
    silhouette_scores,
)


@pytest.fixture
def df_rfm_sample() -> pd.DataFrame:
    """DataFrame RFM sintético com 3 clusters claros."""
    np.random.seed(42)
    # Cluster 0: recentes, frequentes, alto valor
    c0 = pd.DataFrame(
        {
            "customer_unique_id": [f"champ_{i}" for i in range(30)],
            "recency": np.random.randint(1, 30, 30),
            "frequency": np.random.randint(3, 8, 30),
            "monetary": np.random.uniform(500, 1000, 30).round(2),
        }
    )
    # Cluster 1: intermediários
    c1 = pd.DataFrame(
        {
            "customer_unique_id": [f"mid_{i}" for i in range(40)],
            "recency": np.random.randint(60, 150, 40),
            "frequency": np.random.randint(1, 3, 40),
            "monetary": np.random.uniform(100, 400, 40).round(2),
        }
    )
    # Cluster 2: inativos, baixo valor
    c2 = pd.DataFrame(
        {
            "customer_unique_id": [f"lost_{i}" for i in range(30)],
            "recency": np.random.randint(200, 400, 30),
            "frequency": np.random.randint(1, 2, 30),
            "monetary": np.random.uniform(20, 100, 30).round(2),
        }
    )
    return pd.concat([c0, c1, c2], ignore_index=True)


@pytest.fixture
def df_rfm_with_nans(df_rfm_sample: pd.DataFrame) -> pd.DataFrame:
    """DataFrame RFM com NaN em algumas linhas."""
    df = df_rfm_sample.copy()
    df.loc[5, "recency"] = np.nan
    df.loc[10, "monetary"] = np.nan
    df.loc[15, "frequency"] = np.nan
    return df


@pytest.fixture
def X_normalized(df_rfm_sample: pd.DataFrame) -> np.ndarray:
    """Features normalizadas."""
    X, _ = normalizar_features(df_rfm_sample, ["recency", "frequency", "monetary"])
    return X


# =========================================================
# T038 — normalizar_features
# =========================================================


class TestNormalizarFeatures:
    def test_mean_near_zero(self, df_rfm_sample: pd.DataFrame) -> None:
        """T038: Média das features normalizadas é ~0."""
        X, _ = normalizar_features(df_rfm_sample, ["recency", "frequency", "monetary"])
        means = X.mean(axis=0)
        for i, m in enumerate(means):
            assert abs(m) < 1e-10, f"Feature {i}: mean = {m}"

    def test_std_near_one(self, df_rfm_sample: pd.DataFrame) -> None:
        """Desvio padrão das features normalizadas é ~1."""
        X, _ = normalizar_features(df_rfm_sample, ["recency", "frequency", "monetary"])
        stds = X.std(axis=0)
        for i, s in enumerate(stds):
            assert abs(s - 1.0) < 0.05, f"Feature {i}: std = {s}"

    def test_returns_scaler(self, df_rfm_sample: pd.DataFrame) -> None:
        """Retorna o scaler para uso posterior."""
        X, scaler = normalizar_features(
            df_rfm_sample, ["recency", "frequency", "monetary"]
        )
        assert hasattr(scaler, "transform")
        assert hasattr(scaler, "inverse_transform")

    def test_shape_preserved(self, df_rfm_sample: pd.DataFrame) -> None:
        """Shape do array é (n_samples, n_features)."""
        X, _ = normalizar_features(df_rfm_sample, ["recency", "frequency", "monetary"])
        assert X.shape == (len(df_rfm_sample), 3)


# =========================================================
# T039 — elbow_method
# =========================================================


class TestElbowMethod:
    def test_returns_list_of_dicts(self, X_normalized: np.ndarray) -> None:
        """T039: Retorna lista de dicts com k e inertia."""
        results = elbow_method(X_normalized, k_range=range(2, 6))
        assert isinstance(results, list)
        assert len(results) == 4  # k=2,3,4,5
        for r in results:
            assert "k" in r
            assert "inertia" in r

    def test_inertia_decreases(self, X_normalized: np.ndarray) -> None:
        """Inércia decresce conforme k aumenta."""
        results = elbow_method(X_normalized, k_range=range(2, 8))
        inertias = [r["inertia"] for r in results]
        for i in range(1, len(inertias)):
            assert inertias[i] <= inertias[i - 1], (
                f"Inertia aumentou: k={results[i-1]['k']}={inertias[i-1]} > "
                f"k={results[i]['k']}={inertias[i]}"
            )

    def test_inertia_positive(self, X_normalized: np.ndarray) -> None:
        """Todas as inércias são positivas."""
        results = elbow_method(X_normalized, k_range=range(2, 6))
        for r in results:
            assert r["inertia"] > 0

    def test_k_exceeds_samples_is_capped(self) -> None:
        """Se k > n_samples, para no máximo possível."""
        X_small = np.array([[1, 2], [3, 4], [5, 6]])
        results = elbow_method(X_small, k_range=range(2, 10))
        ks = [r["k"] for r in results]
        assert max(ks) <= 3


# =========================================================
# T040 — silhouette_scores
# =========================================================


class TestSilhouetteScores:
    def test_returns_list_of_dicts(self, X_normalized: np.ndarray) -> None:
        """T040: Retorna lista de dicts com k e silhouette."""
        results = silhouette_scores(X_normalized, k_range=range(2, 6))
        assert isinstance(results, list)
        for r in results:
            assert "k" in r
            assert "silhouette" in r

    def test_scores_between_minus1_and_1(self, X_normalized: np.ndarray) -> None:
        """Silhouette scores estão entre -1 e 1."""
        results = silhouette_scores(X_normalized, k_range=range(2, 6))
        for r in results:
            assert (
                -1.0 <= r["silhouette"] <= 1.0
            ), f"k={r['k']}: silhouette={r['silhouette']}"

    def test_positive_for_well_separated_data(self, X_normalized: np.ndarray) -> None:
        """Silhouette é positivo para dados com clusters claros."""
        results = silhouette_scores(X_normalized, k_range=range(2, 6))
        # Pelo menos k=3 deve ter silhouette > 0 (3 clusters claros)
        scores_k3 = [r for r in results if r["k"] == 3]
        assert scores_k3[0]["silhouette"] > 0


# =========================================================
# T041 — rodar_kmeans
# =========================================================


class TestRodarKmeans:
    def test_returns_required_keys(self, X_normalized: np.ndarray) -> None:
        """T041: Resultado contém k, labels, centroids, inertia."""
        result = rodar_kmeans(X_normalized, k=3)
        assert set(result.keys()) == {"k", "labels", "centroids", "inertia"}

    def test_labels_range(self, X_normalized: np.ndarray) -> None:
        """Labels são inteiros de 0 a k-1."""
        result = rodar_kmeans(X_normalized, k=4)
        labels = result["labels"]
        assert set(labels) == {0, 1, 2, 3}

    def test_labels_length(self, X_normalized: np.ndarray) -> None:
        """Número de labels = número de amostras."""
        result = rodar_kmeans(X_normalized, k=3)
        assert len(result["labels"]) == X_normalized.shape[0]

    def test_centroids_shape(self, X_normalized: np.ndarray) -> None:
        """Centroids têm shape (k, n_features)."""
        result = rodar_kmeans(X_normalized, k=3)
        assert result["centroids"].shape == (3, 3)

    def test_reproducible(self, X_normalized: np.ndarray) -> None:
        """Resultados são reproduzíveis com mesmo seed."""
        r1 = rodar_kmeans(X_normalized, k=3, random_state=42)
        r2 = rodar_kmeans(X_normalized, k=3, random_state=42)
        np.testing.assert_array_equal(r1["labels"], r2["labels"])


# =========================================================
# T042-T043 — pipeline_clustering
# =========================================================


class TestPipelineClustering:
    def test_returns_required_keys(self, df_rfm_sample: pd.DataFrame) -> None:
        """T042: pipeline_clustering retorna todas as chaves esperadas."""
        result = pipeline_clustering(df_rfm_sample, k_range=range(2, 6))
        expected = {
            "df_resultado",
            "elbow",
            "silhouette",
            "kmeans",
            "k_otimo",
            "scaler",
            "n_original",
            "n_usado",
        }
        assert set(result.keys()) == expected

    def test_df_resultado_has_cluster_column(self, df_rfm_sample: pd.DataFrame) -> None:
        """DataFrame resultado tem coluna 'cluster'."""
        result = pipeline_clustering(df_rfm_sample, k_range=range(2, 6))
        assert "cluster" in result["df_resultado"].columns

    def test_cluster_labels_valid(self, df_rfm_sample: pd.DataFrame) -> None:
        """Labels de cluster são de 0 a k-1."""
        result = pipeline_clustering(df_rfm_sample, k_range=range(2, 6))
        k = result["k_otimo"]
        labels = set(result["df_resultado"]["cluster"].unique())
        assert labels == set(range(k))

    def test_k_otimo_from_silhouette(self, df_rfm_sample: pd.DataFrame) -> None:
        """k ótimo é o que tem maior silhouette."""
        result = pipeline_clustering(df_rfm_sample, k_range=range(2, 6))
        best_sil = max(result["silhouette"], key=lambda x: x["silhouette"])
        assert result["k_otimo"] == best_sil["k"]

    def test_n_counts(self, df_rfm_sample: pd.DataFrame) -> None:
        """n_original e n_usado corretos (sem NaN = iguais)."""
        result = pipeline_clustering(df_rfm_sample, k_range=range(2, 6))
        assert result["n_original"] == len(df_rfm_sample)
        assert result["n_usado"] == len(df_rfm_sample)

    def test_handles_nans(self, df_rfm_with_nans: pd.DataFrame) -> None:
        """T043: Linhas com NaN são removidas e contagem logada."""
        result = pipeline_clustering(df_rfm_with_nans, k_range=range(2, 6))
        assert result["n_usado"] < result["n_original"]
        assert result["n_usado"] == result["n_original"] - 3
        assert "cluster" in result["df_resultado"].columns

    def test_insufficient_data(self) -> None:
        """DataFrame com < 2 linhas retorna resultado vazio."""
        df_tiny = pd.DataFrame(
            {
                "recency": [10],
                "frequency": [1],
                "monetary": [50.0],
            }
        )
        result = pipeline_clustering(df_tiny)
        assert result["kmeans"] is None
        assert result["k_otimo"] is None
        assert result["elbow"] == []

    def test_finds_3_clusters_in_clear_data(self, df_rfm_sample: pd.DataFrame) -> None:
        """Encontra ~3 clusters em dados com 3 grupos claros."""
        result = pipeline_clustering(df_rfm_sample, k_range=range(2, 8))
        # k_otimo deve estar perto de 3
        assert 2 <= result["k_otimo"] <= 5


# =========================================================
# Predição de atraso — fixtures e testes (T044-T050)
# =========================================================

from pipeline.analyze.predicao import (
    avaliar_modelo,
    criar_features,
    pipeline_predicao,
    preparar_dados,
    treinar_modelo,
)


@pytest.fixture(scope="session")
def db_path_fixture(sample_db, tmp_path_factory: pytest.TempPathFactory) -> str:
    """Exporta sample_db pra arquivo temporário e retorna o path.

    Necessário porque criar_features() abre sua própria conexão.
    """
    db_file = tmp_path_factory.mktemp("duckdb") / "test_olist.duckdb"
    dest = duckdb.connect(str(db_file))
    # Copiar todas as tabelas do sample_db in-memory pro arquivo
    tables = sample_db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    ).fetchall()
    for (table_name,) in tables:
        df_table = sample_db.execute(f"SELECT * FROM {table_name}").fetchdf()
        dest.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df_table")
    dest.close()
    return str(db_file)


@pytest.fixture(scope="session")
def df_features(db_path_fixture: str) -> pd.DataFrame:
    """DataFrame com features extraídas do banco de teste."""
    return criar_features(db_path_fixture)


@pytest.fixture(scope="session")
def dados_split(df_features: pd.DataFrame) -> tuple:
    """Dados já splitados pra treino e teste."""
    return preparar_dados(df_features)


# =========================================================
# T044 — criar_features
# =========================================================


class TestCriarFeatures:
    def test_only_delivered_orders(self, df_features: pd.DataFrame) -> None:
        """T044: Resultado contém apenas pedidos delivered."""
        # Todos os registros no df devem ter target 0 ou 1 (nenhum NaN)
        assert df_features["atraso"].isin([0, 1]).all()
        assert len(df_features) > 0

    def test_target_is_binary(self, df_features: pd.DataFrame) -> None:
        """Target variable é binária (0 ou 1)."""
        assert set(df_features["atraso"].unique()).issubset({0, 1})

    def test_required_columns_present(self, df_features: pd.DataFrame) -> None:
        """DataFrame tem todas as colunas esperadas."""
        expected = {
            "order_id",
            "peso_g",
            "frete",
            "preco",
            "estado_cliente",
            "distancia_estimada_dias",
            "volume_cm3",
            "atraso",
        }
        assert expected == set(df_features.columns)

    def test_distancia_estimada_positive(self, df_features: pd.DataFrame) -> None:
        """Distância estimada em dias é positiva (compra antes da estimativa)."""
        valid = df_features["distancia_estimada_dias"].dropna()
        assert (valid > 0).all()

    def test_no_non_delivered_orders(
        self, sample_db, df_features: pd.DataFrame
    ) -> None:
        """Nenhum order_id de pedido não-delivered aparece no resultado."""
        non_delivered = sample_db.execute(
            "SELECT order_id FROM orders WHERE order_status != 'delivered'"
        ).fetchdf()
        overlap = set(df_features["order_id"]) & set(non_delivered["order_id"])
        assert len(overlap) == 0


# =========================================================
# T045 — preparar_dados
# =========================================================


class TestPrepararDados:
    def test_split_sizes(self, dados_split: tuple) -> None:
        """T045: Split é ~80/20."""
        X_train, X_test, y_train, y_test, _ = dados_split
        total = len(X_train) + len(X_test)
        ratio_train = len(X_train) / total
        assert 0.75 <= ratio_train <= 0.85

    def test_stratified_split(self, dados_split: tuple) -> None:
        """Split estratificado preserva proporção do target."""
        X_train, X_test, y_train, y_test, _ = dados_split
        prop_train = y_train.mean()
        prop_test = y_test.mean()
        # Proporções devem ser próximas (tolerância de 10pp)
        assert abs(prop_train - prop_test) < 0.10

    def test_returns_feature_names(self, dados_split: tuple) -> None:
        """Retorna lista de nomes das features."""
        _, _, _, _, feature_names = dados_split
        assert isinstance(feature_names, list)
        assert len(feature_names) > 0
        assert "atraso" not in feature_names
        assert "order_id" not in feature_names

    def test_no_nans_in_output(self, dados_split: tuple) -> None:
        """Dados de saída não contêm NaN."""
        X_train, X_test, y_train, y_test, _ = dados_split
        assert not np.isnan(X_train).any()
        assert not np.isnan(X_test).any()
        assert not np.isnan(y_train).any()
        assert not np.isnan(y_test).any()

    def test_feature_count_matches(self, dados_split: tuple) -> None:
        """Número de features em X corresponde à lista de nomes."""
        X_train, X_test, _, _, feature_names = dados_split
        assert X_train.shape[1] == len(feature_names)
        assert X_test.shape[1] == len(feature_names)


# =========================================================
# T046-T047 — treinar_modelo
# =========================================================


class TestTreinarModelo:
    def test_logistic_regression(self, dados_split: tuple) -> None:
        """T046: Treina LogisticRegression com class_weight balanced."""
        X_train, _, y_train, _, _ = dados_split
        modelo = treinar_modelo(X_train, y_train, modelo="logistic")
        assert hasattr(modelo, "predict")
        assert hasattr(modelo, "predict_proba")
        assert modelo.class_weight == "balanced"

    def test_random_forest(self, dados_split: tuple) -> None:
        """T047: Treina RandomForestClassifier com class_weight balanced."""
        X_train, _, y_train, _, _ = dados_split
        modelo = treinar_modelo(X_train, y_train, modelo="random_forest")
        assert hasattr(modelo, "predict")
        assert hasattr(modelo, "feature_importances_")
        assert modelo.class_weight == "balanced"

    def test_invalid_model_raises(self, dados_split: tuple) -> None:
        """Modelo inválido levanta ValueError."""
        X_train, _, y_train, _, _ = dados_split
        with pytest.raises(ValueError, match="não suportado"):
            treinar_modelo(X_train, y_train, modelo="svm")

    def test_reproducible(self, dados_split: tuple) -> None:
        """Resultados são reproduzíveis com mesmo seed."""
        X_train, X_test, y_train, _, _ = dados_split
        m1 = treinar_modelo(X_train, y_train, modelo="logistic", random_state=42)
        m2 = treinar_modelo(X_train, y_train, modelo="logistic", random_state=42)
        p1 = m1.predict(X_test)
        p2 = m2.predict(X_test)
        np.testing.assert_array_equal(p1, p2)


# =========================================================
# T048 — avaliar_modelo
# =========================================================


class TestAvaliarModelo:
    def test_returns_required_keys(self, dados_split: tuple) -> None:
        """T048: Métricas incluem accuracy, precision, recall, F1, AUC-ROC."""
        X_train, X_test, y_train, y_test, _ = dados_split
        modelo = treinar_modelo(X_train, y_train, modelo="logistic")
        metricas = avaliar_modelo(modelo, X_test, y_test)
        expected_keys = {
            "accuracy",
            "precision",
            "recall",
            "f1",
            "auc_roc",
            "confusion_matrix",
            "classification_report",
        }
        assert set(metricas.keys()) == expected_keys

    def test_metrics_in_valid_range(self, dados_split: tuple) -> None:
        """Métricas estão entre 0 e 1."""
        X_train, X_test, y_train, y_test, _ = dados_split
        modelo = treinar_modelo(X_train, y_train, modelo="logistic")
        metricas = avaliar_modelo(modelo, X_test, y_test)
        for key in ["accuracy", "precision", "recall", "f1"]:
            assert 0.0 <= metricas[key] <= 1.0, f"{key}={metricas[key]}"
        if metricas["auc_roc"] is not None:
            assert 0.0 <= metricas["auc_roc"] <= 1.0

    def test_confusion_matrix_shape(self, dados_split: tuple) -> None:
        """Confusion matrix é 2x2."""
        X_train, X_test, y_train, y_test, _ = dados_split
        modelo = treinar_modelo(X_train, y_train, modelo="logistic")
        metricas = avaliar_modelo(modelo, X_test, y_test)
        cm = metricas["confusion_matrix"]
        assert len(cm) == 2
        assert len(cm[0]) == 2

    def test_classification_report_is_string(self, dados_split: tuple) -> None:
        """classification_report é uma string."""
        X_train, X_test, y_train, y_test, _ = dados_split
        modelo = treinar_modelo(X_train, y_train, modelo="logistic")
        metricas = avaliar_modelo(modelo, X_test, y_test)
        assert isinstance(metricas["classification_report"], str)
        assert "precision" in metricas["classification_report"]


# =========================================================
# T049-T050 — pipeline_predicao
# =========================================================

import duckdb


class TestPipelinePredicao:
    def test_returns_required_keys(self, db_path_fixture: str) -> None:
        """T049: pipeline_predicao retorna todas as chaves esperadas."""
        result = pipeline_predicao(db_path_fixture)
        expected = {
            "metricas_logistic",
            "metricas_rf",
            "feature_importances",
            "feature_names",
            "n_original",
            "n_usado",
            "proporcao_atraso",
        }
        assert set(result.keys()) == expected

    def test_both_models_evaluated(self, db_path_fixture: str) -> None:
        """Ambos os modelos (logistic e RF) são avaliados."""
        result = pipeline_predicao(db_path_fixture)
        assert result["metricas_logistic"] is not None
        assert result["metricas_rf"] is not None
        assert "accuracy" in result["metricas_logistic"]
        assert "accuracy" in result["metricas_rf"]

    def test_feature_importances_returned(self, db_path_fixture: str) -> None:
        """T050: Feature importances são retornadas e somam ~1."""
        result = pipeline_predicao(db_path_fixture)
        fi = result["feature_importances"]
        assert isinstance(fi, list)
        assert len(fi) > 0
        total = sum(item["importance"] for item in fi)
        assert 0.95 <= total <= 1.05  # Tolerância por arredondamento

    def test_feature_importances_sorted(self, db_path_fixture: str) -> None:
        """Feature importances estão ordenadas por importância decrescente."""
        result = pipeline_predicao(db_path_fixture)
        fi = result["feature_importances"]
        importances = [item["importance"] for item in fi]
        assert importances == sorted(importances, reverse=True)

    def test_n_counts_consistent(self, db_path_fixture: str) -> None:
        """n_original >= n_usado > 0."""
        result = pipeline_predicao(db_path_fixture)
        assert result["n_original"] > 0
        assert result["n_usado"] > 0
        assert result["n_original"] >= result["n_usado"]

    def test_proporcao_atraso_valid(self, db_path_fixture: str) -> None:
        """Proporção de atraso está entre 0 e 1."""
        result = pipeline_predicao(db_path_fixture)
        assert 0.0 <= result["proporcao_atraso"] <= 1.0

    def test_insufficient_data_returns_none(
        self, tmp_path_factory: pytest.TempPathFactory
    ) -> None:
        """Banco sem dados suficientes retorna resultado com Nones."""
        db_file = tmp_path_factory.mktemp("empty_db") / "empty.duckdb"
        con = duckdb.connect(str(db_file))
        # Criar tabelas mínimas vazias
        con.execute("""
            CREATE TABLE orders (
                order_id VARCHAR, customer_id VARCHAR, order_status VARCHAR,
                order_purchase_timestamp TIMESTAMP, order_approved_at TIMESTAMP,
                order_delivered_carrier_date TIMESTAMP,
                order_delivered_customer_date TIMESTAMP,
                order_estimated_delivery_date TIMESTAMP
            )
        """)
        con.execute("""
            CREATE TABLE order_items (
                order_id VARCHAR, order_item_id INTEGER, product_id VARCHAR,
                seller_id VARCHAR, shipping_limit_date TIMESTAMP,
                price DECIMAL(10,2), freight_value DECIMAL(10,2)
            )
        """)
        con.execute("""
            CREATE TABLE products (
                product_id VARCHAR, product_category_name VARCHAR,
                product_name_length INTEGER, product_description_length INTEGER,
                product_photos_qty INTEGER, product_weight_g INTEGER,
                product_length_cm INTEGER, product_height_cm INTEGER,
                product_width_cm INTEGER
            )
        """)
        con.execute("""
            CREATE TABLE customers (
                customer_id VARCHAR, customer_unique_id VARCHAR,
                customer_zip_code_prefix VARCHAR, customer_city VARCHAR,
                customer_state VARCHAR
            )
        """)
        con.close()

        result = pipeline_predicao(str(db_file))
        assert result["metricas_logistic"] is None
        assert result["metricas_rf"] is None
        assert result["feature_importances"] is None
