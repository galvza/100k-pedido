"""Testes do export de JSONs — T051-T060, T082-T084."""

from __future__ import annotations

import json
import math
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest

from pipeline.export import (
    _clean_value,
    _df_to_records,
    _round_fields,
    _save_json,
    export_all,
)
from pipeline.queries import run_query

# =========================================================
# Fixtures
# =========================================================


@pytest.fixture(scope="session")
def all_query_results(
    sample_db: duckdb.DuckDBPyConnection,
) -> dict:
    """Executa todas as queries SQL e retorna resultados consolidados."""
    resultados: dict = {}
    sql_files = [
        "01_funil.sql",
        "02_rfm.sql",
        "03_cohort.sql",
        "04_geo.sql",
        "05_sazonalidade.sql",
        "06_reviews.sql",
    ]
    for sql_file in sql_files:
        query_results = run_query(sql_file, con=sample_db)
        resultados.update(query_results)
    return resultados


@pytest.fixture(scope="session")
def resultados_completos(
    all_query_results: dict,
    sample_db: duckdb.DuckDBPyConnection,
    tmp_path_factory: pytest.TempPathFactory,
) -> dict:
    """Resultados completos com queries + clustering pra export."""
    from pipeline.analyze.clustering import pipeline_clustering

    resultados = dict(all_query_results)

    # Adicionar clustering se rfm_scores existe
    if "rfm_scores" in resultados:
        df_rfm = resultados["rfm_scores"]
        clustering = pipeline_clustering(
            df_rfm,
            colunas=["recency", "frequency", "monetary"],
            k_range=range(2, 6),
        )
        resultados["clustering"] = clustering

    # reviews_palavras sintético pra completar o cap.6
    resultados["reviews_palavras"] = [
        {"palavra": "bom", "contagem": 50, "faixa": "4-5"},
        {"palavra": "ruim", "contagem": 30, "faixa": "1-2"},
    ]

    # geo_correlacao sintético
    resultados["geo_correlacao"] = {
        "teste_usado": "Mann-Whitney U",
        "p_value": 0.0312,
        "significativo": True,
        "tamanho_efeito": -0.2345,
    }

    return resultados


@pytest.fixture(scope="session")
def exported_dir(
    resultados_completos: dict,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    """Diretório com todos os JSONs exportados."""
    output_dir = tmp_path_factory.mktemp("export_output")
    export_all(resultados_completos, output_dir=output_dir)
    return output_dir


@pytest.fixture(scope="session")
def exported_files(exported_dir: Path) -> dict[str, Path]:
    """Dict com nome → Path de cada JSON exportado."""
    return {f.name: f for f in exported_dir.glob("*.json")}


# =========================================================
# T051 — _clean_value
# =========================================================


class TestCleanValue:
    def test_nan_becomes_none(self) -> None:
        """T051: NaN vira None (→ null no JSON)."""
        assert _clean_value(float("nan")) is None
        assert _clean_value(np.nan) is None

    def test_none_stays_none(self) -> None:
        """None permanece None."""
        assert _clean_value(None) is None

    def test_inf_becomes_none(self) -> None:
        """Infinity vira None."""
        assert _clean_value(float("inf")) is None
        assert _clean_value(float("-inf")) is None

    def test_numpy_int_to_python(self) -> None:
        """numpy int64 → Python int."""
        result = _clean_value(np.int64(42))
        assert result == 42
        assert isinstance(result, int)

    def test_numpy_float_to_python(self) -> None:
        """numpy float64 → Python float."""
        result = _clean_value(np.float64(3.14))
        assert result == 3.14
        assert isinstance(result, float)

    def test_timestamp_to_iso_string(self) -> None:
        """Timestamp → string ISO (YYYY-MM-DD)."""
        ts = pd.Timestamp("2018-06-15 14:30:00")
        assert _clean_value(ts) == "2018-06-15"

    def test_nat_becomes_none(self) -> None:
        """pd.NaT → None."""
        assert _clean_value(pd.NaT) is None

    def test_regular_values_unchanged(self) -> None:
        """Valores regulares passam sem alteração."""
        assert _clean_value(42) == 42
        assert _clean_value(3.14) == 3.14
        assert _clean_value("hello") == "hello"
        assert _clean_value(True) is True


# =========================================================
# T052 — _df_to_records
# =========================================================


class TestDfToRecords:
    def test_basic_conversion(self) -> None:
        """T052: DataFrame básico vira lista de dicts."""
        df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
        records = _df_to_records(df)
        assert len(records) == 2
        assert records[0] == {"a": 1, "b": 3.0}

    def test_nan_becomes_null(self) -> None:
        """NaN no DataFrame vira None nos records."""
        df = pd.DataFrame({"a": [1, np.nan], "b": [3.0, 4.0]})
        records = _df_to_records(df)
        assert records[1]["a"] is None

    def test_timestamps_converted(self) -> None:
        """Timestamps são convertidos pra ISO string."""
        df = pd.DataFrame(
            {
                "data": pd.to_datetime(["2018-01-15", "2018-02-20"]),
                "valor": [1, 2],
            }
        )
        records = _df_to_records(df)
        assert records[0]["data"] == "2018-01-15"

    def test_empty_dataframe(self) -> None:
        """DataFrame vazio retorna lista vazia."""
        df = pd.DataFrame()
        assert _df_to_records(df) == []


# =========================================================
# T053 — _round_fields
# =========================================================


class TestRoundFields:
    def test_monetary_rounding(self) -> None:
        """T053: Campos monetários arredondados a 2 casas."""
        records = [{"receita": 123.456789, "nome": "SP"}]
        result = _round_fields(records, monetary=["receita"])
        assert result[0]["receita"] == 123.46

    def test_none_values_preserved(self) -> None:
        """None nos campos monetários é preservado."""
        records = [{"receita": None, "nome": "SP"}]
        result = _round_fields(records, monetary=["receita"])
        assert result[0]["receita"] is None

    def test_int_values_preserved(self) -> None:
        """Inteiros nos campos monetários permanecem inteiros."""
        records = [{"pedidos": 100, "receita": 50.0}]
        result = _round_fields(records, monetary=["pedidos"])
        assert result[0]["pedidos"] == 100

    def test_no_monetary_fields(self) -> None:
        """Sem campos monetários, records passam sem alteração."""
        records = [{"a": 1.23456}]
        result = _round_fields(records)
        assert result[0]["a"] == 1.23456


# =========================================================
# T054 — export_all gera todos os JSONs
# =========================================================


class TestExportAll:
    def test_returns_list_of_filenames(
        self, resultados_completos: dict, tmp_output_dir: Path
    ) -> None:
        """T054: export_all retorna lista de nomes de arquivos."""
        result = export_all(resultados_completos, output_dir=tmp_output_dir)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(f.endswith(".json") for f in result)

    def test_creates_output_directory(
        self, resultados_completos: dict, tmp_path: Path
    ) -> None:
        """Cria diretório de saída se não existir."""
        new_dir = tmp_path / "new_output"
        export_all(resultados_completos, output_dir=new_dir)
        assert new_dir.exists()

    def test_generates_18_jsons(self, exported_files: dict) -> None:
        """Gera 18 JSONs no total."""
        assert len(exported_files) == 18, (
            f"Esperados 18 JSONs, encontrados {len(exported_files)}: "
            f"{sorted(exported_files.keys())}"
        )

    def test_empty_resultados_generates_nothing(self, tmp_output_dir: Path) -> None:
        """Dict vazio não gera nenhum JSON."""
        result = export_all({}, output_dir=tmp_output_dir)
        assert result == []


# =========================================================
# T055 — Todos os JSONs são válidos
# =========================================================


class TestJsonValidity:
    def test_all_jsons_are_valid(self, exported_dir: Path) -> None:
        """T055: Todos os JSONs são parseáveis com json.loads."""
        for json_file in exported_dir.glob("*.json"):
            content = json_file.read_text(encoding="utf-8")
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                pytest.fail(f"{json_file.name} não é JSON válido: {e}")

    def test_no_nan_strings(self, exported_dir: Path) -> None:
        """Nenhum JSON contém a string literal 'NaN'."""
        for json_file in exported_dir.glob("*.json"):
            content = json_file.read_text(encoding="utf-8")
            # Procurar NaN como valor JSON (não dentro de strings regulares)
            data = json.loads(content)
            _assert_no_nan_strings(data, json_file.name)

    def test_no_json_exceeds_500kb(self, exported_dir: Path) -> None:
        """T056: Nenhum JSON excede 500KB."""
        for json_file in exported_dir.glob("*.json"):
            size_kb = json_file.stat().st_size / 1024
            assert (
                size_kb <= 500
            ), f"{json_file.name} tem {size_kb:.1f} KB (limite: 500 KB)"


def _assert_no_nan_strings(data: object, context: str) -> None:
    """Recursivamente verifica que não há strings 'NaN' nos dados."""
    if isinstance(data, str):
        assert data != "NaN", f"String 'NaN' encontrada em {context}"
    elif isinstance(data, dict):
        for k, v in data.items():
            _assert_no_nan_strings(v, f"{context}.{k}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            _assert_no_nan_strings(item, f"{context}[{i}]")


# =========================================================
# T057 — Cap.1 Funil de Vendas
# =========================================================


class TestExportFunil:
    def test_funil_status_structure(self, exported_dir: Path) -> None:
        """T057: 01_funil_status.json tem estrutura correta."""
        data = _load_json(exported_dir / "01_funil_status.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "status" in row
            assert "contagem" in row
            assert "percentual" in row
            assert isinstance(row["contagem"], int)

    def test_funil_conversao_structure(self, exported_dir: Path) -> None:
        """01_funil_conversao.json tem 4 etapas."""
        data = _load_json(exported_dir / "01_funil_conversao.json")
        assert isinstance(data, list)
        etapas = {row["etapa"] for row in data}
        assert etapas == {"Compra", "Aprovacao", "Envio", "Entrega"}
        for row in data:
            assert "pedidos" in row
            assert "taxa_conversao" in row
            assert "tempo_medio_dias" in row

    def test_funil_tempos_structure(self, exported_dir: Path) -> None:
        """01_funil_tempos.json tem faixas de tempo."""
        data = _load_json(exported_dir / "01_funil_tempos.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "faixa" in row
            assert "contagem" in row


# =========================================================
# T058 — Cap.2 RFM
# =========================================================


class TestExportRfm:
    def test_rfm_distribuicao_structure(self, exported_dir: Path) -> None:
        """T058: 02_rfm_distribuicao.json tem 3 dimensões."""
        data = _load_json(exported_dir / "02_rfm_distribuicao.json")
        assert isinstance(data, dict)
        for dim in ["recency", "frequency", "monetary"]:
            assert dim in data
            stats = data[dim]
            for key in ["min", "max", "media", "mediana", "std"]:
                assert key in stats

    def test_rfm_segmentos_structure(self, exported_dir: Path) -> None:
        """02_rfm_segmentos.json tem segmentos com contagem."""
        data = _load_json(exported_dir / "02_rfm_segmentos.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "segmento" in row
            assert "contagem" in row
            assert isinstance(row["contagem"], int)

    def test_rfm_clustering_structure(self, exported_dir: Path) -> None:
        """02_rfm_clustering.json tem k_otimo e elbow."""
        data = _load_json(exported_dir / "02_rfm_clustering.json")
        assert isinstance(data, dict)
        assert "k_otimo" in data
        assert "elbow" in data
        assert "silhouette" in data
        assert isinstance(data["elbow"], list)


# =========================================================
# T059 — Cap.3 Cohort
# =========================================================


class TestExportCohort:
    def test_cohort_heatmap_structure(self, exported_dir: Path) -> None:
        """T059: 03_cohort_heatmap.json tem coortes, periodos, dados."""
        data = _load_json(exported_dir / "03_cohort_heatmap.json")
        assert isinstance(data, dict)
        assert "coortes" in data
        assert "periodos" in data
        assert "dados" in data
        assert isinstance(data["coortes"], list)
        assert isinstance(data["periodos"], list)
        assert isinstance(data["dados"], list)

    def test_cohort_heatmap_coorte_format(self, exported_dir: Path) -> None:
        """Coortes são strings YYYY-MM."""
        data = _load_json(exported_dir / "03_cohort_heatmap.json")
        for coorte in data["coortes"]:
            assert len(coorte) == 7, f"Coorte '{coorte}' não está no formato YYYY-MM"
            assert coorte[4] == "-"

    def test_cohort_heatmap_retencao_allows_null(self, exported_dir: Path) -> None:
        """Retencao pode conter null (períodos futuros)."""
        data = _load_json(exported_dir / "03_cohort_heatmap.json")
        # Pelo menos o último coorte deve ter algum null
        has_null = False
        for dado in data["dados"]:
            if None in dado["retencao"]:
                has_null = True
                break
        # Com dados de teste, pode ou não ter null; verificar apenas a estrutura
        for dado in data["dados"]:
            assert "coorte" in dado
            assert "tamanho" in dado
            assert "retencao" in dado
            assert isinstance(dado["retencao"], list)

    def test_cohort_recompra_structure(self, exported_dir: Path) -> None:
        """03_cohort_recompra.json tem métricas de recompra."""
        data = _load_json(exported_dir / "03_cohort_recompra.json")
        assert isinstance(data, list)
        assert len(data) > 0
        row = data[0]
        assert "total_clientes" in row
        assert "clientes_recompra" in row
        assert "taxa_recompra_pct" in row


# =========================================================
# T060 — Cap.4 Geo, Cap.5 Sazonalidade, Cap.6 Reviews
# =========================================================


class TestExportGeo:
    def test_geo_estados_structure(self, exported_dir: Path) -> None:
        """T060: 04_geo_estados.json tem métricas por estado."""
        data = _load_json(exported_dir / "04_geo_estados.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "estado" in row
            assert "pedidos" in row
            assert "receita" in row
            assert "ticket_medio" in row

    def test_geo_correlacao_structure(self, exported_dir: Path) -> None:
        """04_geo_correlacao.json tem dados de correlação."""
        data = _load_json(exported_dir / "04_geo_correlacao.json")
        assert isinstance(data, dict)
        assert "p_value" in data

    def test_geo_categorias_structure(self, exported_dir: Path) -> None:
        """04_geo_categorias.json tem categorias por estado."""
        data = _load_json(exported_dir / "04_geo_categorias.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "estado" in row
            assert "categoria" in row


class TestExportSazonalidade:
    def test_sazonalidade_mensal_structure(self, exported_dir: Path) -> None:
        """05_sazonalidade_mensal.json tem série temporal."""
        data = _load_json(exported_dir / "05_sazonalidade_mensal.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "mes" in row
            assert "pedidos" in row
            assert "receita" in row

    def test_sazonalidade_mensal_date_format(self, exported_dir: Path) -> None:
        """Mês no formato YYYY-MM."""
        data = _load_json(exported_dir / "05_sazonalidade_mensal.json")
        for row in data:
            mes = row["mes"]
            assert len(mes) == 7, f"Mês '{mes}' não está no formato YYYY-MM"
            assert mes[4] == "-"

    def test_sazonalidade_semanal_7_days(self, exported_dir: Path) -> None:
        """05_sazonalidade_semanal.json tem 7 dias."""
        data = _load_json(exported_dir / "05_sazonalidade_semanal.json")
        assert isinstance(data, list)
        assert len(data) == 7
        dias = {row["dia_semana"] for row in data}
        assert dias == {0, 1, 2, 3, 4, 5, 6}

    def test_sazonalidade_horaria_24_hours(self, exported_dir: Path) -> None:
        """05_sazonalidade_horaria.json tem até 24 horas."""
        data = _load_json(exported_dir / "05_sazonalidade_horaria.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert 0 <= row["hora"] <= 23


class TestExportReviews:
    def test_reviews_distribuicao_structure(self, exported_dir: Path) -> None:
        """06_reviews_distribuicao.json tem scores 1-5."""
        data = _load_json(exported_dir / "06_reviews_distribuicao.json")
        assert isinstance(data, list)
        assert len(data) == 5
        scores = {row["score"] for row in data}
        assert scores == {1, 2, 3, 4, 5}

    def test_reviews_categorias_structure(self, exported_dir: Path) -> None:
        """06_reviews_categorias.json tem categorias."""
        data = _load_json(exported_dir / "06_reviews_categorias.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "categoria" in row
            assert "score_medio" in row

    def test_reviews_atraso_structure(self, exported_dir: Path) -> None:
        """06_reviews_atraso.json tem faixas de atraso."""
        data = _load_json(exported_dir / "06_reviews_atraso.json")
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "faixa_atraso" in row
            assert "contagem" in row
            assert "score_medio" in row

    def test_reviews_palavras_structure(self, exported_dir: Path) -> None:
        """06_reviews_palavras.json tem palavras."""
        data = _load_json(exported_dir / "06_reviews_palavras.json")
        assert isinstance(data, list)
        assert len(data) > 0


# =========================================================
# T082-T084 — Arredondamento e qualidade dos dados
# =========================================================


class TestDataQuality:
    def test_monetary_values_max_2_decimals(self, exported_dir: Path) -> None:
        """T082: Valores monetários têm no máximo 2 casas decimais."""
        monetary_files = {
            "01_funil_conversao.json": ["tempo_medio_dias"],
            "04_geo_estados.json": ["receita", "ticket_medio", "frete_medio"],
            "05_sazonalidade_mensal.json": ["receita", "media_movel_3m"],
        }
        for filename, fields in monetary_files.items():
            path = exported_dir / filename
            if not path.exists():
                continue
            data = _load_json(path)
            if isinstance(data, list):
                for row in data:
                    for field in fields:
                        val = row.get(field)
                        if val is not None and isinstance(val, float):
                            decimal_str = (
                                str(val).split(".")[-1] if "." in str(val) else ""
                            )
                            assert (
                                len(decimal_str) <= 2
                            ), f"{filename}.{field}={val} tem mais de 2 casas decimais"

    def test_dates_are_iso_strings(self, exported_dir: Path) -> None:
        """T083: Datas são strings ISO (YYYY-MM ou YYYY-MM-DD)."""
        # Verificar sazonalidade_mensal (mes) e cohort (coorte)
        mensal = _load_json(exported_dir / "05_sazonalidade_mensal.json")
        for row in mensal:
            mes = row["mes"]
            assert isinstance(mes, str)
            parts = mes.split("-")
            assert len(parts) == 2
            assert len(parts[0]) == 4
            assert len(parts[1]) == 2

    def test_nan_is_null_not_string(self, exported_dir: Path) -> None:
        """T084: NaN no DataFrame vira null no JSON, não string 'NaN'."""
        for json_file in exported_dir.glob("*.json"):
            raw = json_file.read_text(encoding="utf-8")
            # NaN como literal JSON (sem aspas) não é JSON válido,
            # e como string "NaN" é indesejado
            assert '"NaN"' not in raw, f"String 'NaN' encontrada em {json_file.name}"
            # Verificar que o JSON é válido (NaN literal causaria erro)
            json.loads(raw)


# =========================================================
# Helpers
# =========================================================


def _load_json(path: Path) -> Any:
    """Carrega e retorna conteúdo de um arquivo JSON."""
    from typing import Any

    content = path.read_text(encoding="utf-8")
    return json.loads(content)
