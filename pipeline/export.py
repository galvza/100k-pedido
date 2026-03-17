"""Converte DataFrames de todos os capítulos em JSONs otimizados pro dashboard.

Cada capítulo gera 1-4 JSONs em data/output/. Otimizações:
- Valores monetários arredondados a 2 casas decimais
- Percentuais a 4 casas
- NaN → null (não "NaN" string)
- Datas → ISO string (YYYY-MM-DD ou YYYY-MM)
- Sem campos desnecessários (IDs individuais de cliente, etc.)

Uso:
    python -m pipeline.export
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pipeline.config import DATA_OUTPUT_DIR

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Helpers de serialização
# --------------------------------------------------------------------------- #


def _clean_value(v: Any) -> Any:
    """Converte valor individual pra JSON-safe.

    - NaN/None → None (vira null no JSON)
    - numpy int/float → Python nativo
    - Timestamp/date → ISO string
    - ndarray → lista
    """
    if v is None:
        return None
    if isinstance(v, type(pd.NaT)):
        return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        f = float(v)
        return None if math.isnan(f) or math.isinf(f) else f
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, (pd.Timestamp, np.datetime64)):
        ts = pd.Timestamp(v)
        if pd.isna(ts):
            return None
        return ts.isoformat()[:10]  # YYYY-MM-DD
    if isinstance(v, np.ndarray):
        return [_clean_value(x) for x in v.tolist()]
    return v


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Converte DataFrame em lista de dicts JSON-safe."""
    records = df.to_dict(orient="records")
    return [{k: _clean_value(v) for k, v in row.items()} for row in records]


def _round_monetary(v: Any) -> Any:
    """Arredonda valor monetário pra 2 casas."""
    if v is None:
        return None
    if isinstance(v, (int, np.integer)):
        return v
    if isinstance(v, (float, np.floating)):
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 2)
    return v


def _round_fields(records: list[dict], monetary: list[str] | None = None) -> list[dict]:
    """Aplica arredondamento a campos monetários nos records."""
    if not monetary:
        return records
    result = []
    for row in records:
        new_row = dict(row)
        for field in monetary:
            if field in new_row:
                new_row[field] = _round_monetary(new_row[field])
        result.append(new_row)
    return result


def _save_json(data: Any, path: Path) -> None:
    """Salva dados como JSON com encoding UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    size_kb = path.stat().st_size / 1024
    logger.info("  Salvo: %s (%.1f KB)", path.name, size_kb)
    if size_kb > 500:
        logger.warning("  AVISO: %s excede 500KB (%.1f KB)", path.name, size_kb)


# --------------------------------------------------------------------------- #
# Exportadores por capítulo
# --------------------------------------------------------------------------- #


def _export_cap1_funil(resultados: dict, output_dir: Path) -> list[str]:
    """Cap.1: Funil de Vendas — 3 JSONs."""
    paths = []

    # 01_funil_status.json
    if "funil_status" in resultados:
        records = _df_to_records(resultados["funil_status"])
        records = _round_fields(records, monetary=["percentual"])
        _save_json(records, output_dir / "01_funil_status.json")
        paths.append("01_funil_status.json")

    # 01_funil_conversao.json
    if "funil_conversao" in resultados:
        records = _df_to_records(resultados["funil_conversao"])
        records = _round_fields(records, monetary=["tempo_medio_dias"])
        _save_json(records, output_dir / "01_funil_conversao.json")
        paths.append("01_funil_conversao.json")

    # 01_funil_tempos.json
    if "funil_tempos" in resultados:
        records = _df_to_records(resultados["funil_tempos"])
        records = _round_fields(records, monetary=["media_dias_na_faixa"])
        _save_json(records, output_dir / "01_funil_tempos.json")
        paths.append("01_funil_tempos.json")

    return paths


def _export_cap2_rfm(resultados: dict, output_dir: Path) -> list[str]:
    """Cap.2: RFM Segmentation — 3 JSONs."""
    paths = []

    # 02_rfm_distribuicao.json — histogramas de R, F, M baseados em rfm_scores
    if "rfm_scores" in resultados:
        df = resultados["rfm_scores"]
        distribuicao = {}
        for col in ["recency", "frequency", "monetary"]:
            if col in df.columns:
                values = df[col].dropna()
                distribuicao[col] = {
                    "min": _clean_value(round(float(values.min()), 2)),
                    "max": _clean_value(round(float(values.max()), 2)),
                    "media": _clean_value(round(float(values.mean()), 2)),
                    "mediana": _clean_value(round(float(values.median()), 2)),
                    "std": _clean_value(round(float(values.std()), 2)),
                    "q1": _clean_value(round(float(values.quantile(0.25)), 2)),
                    "q3": _clean_value(round(float(values.quantile(0.75)), 2)),
                }
        _save_json(distribuicao, output_dir / "02_rfm_distribuicao.json")
        paths.append("02_rfm_distribuicao.json")

    # 02_rfm_segmentos.json
    if "rfm_segmentos" in resultados:
        records = _df_to_records(resultados["rfm_segmentos"])
        records = _round_fields(records, monetary=["monetario_medio"])
        _save_json(records, output_dir / "02_rfm_segmentos.json")
        paths.append("02_rfm_segmentos.json")

    # 02_rfm_clustering.json — resultados do K-Means
    if "clustering" in resultados and resultados["clustering"] is not None:
        cl = resultados["clustering"]
        clustering_data = {
            "k_otimo": cl.get("k_otimo"),
            "n_usado": cl.get("n_usado"),
            "n_original": cl.get("n_original"),
            "elbow": cl.get("elbow", []),
            "silhouette": cl.get("silhouette", []),
        }
        # Centroids do kmeans result
        if cl.get("kmeans") and cl["kmeans"].get("centroids") is not None:
            centroids = cl["kmeans"]["centroids"]
            if isinstance(centroids, np.ndarray):
                centroids = centroids.tolist()
            clustering_data["centroids"] = [
                [round(float(v), 4) for v in row] for row in centroids
            ]
        _save_json(clustering_data, output_dir / "02_rfm_clustering.json")
        paths.append("02_rfm_clustering.json")

    return paths


def _export_cap3_cohort(resultados: dict, output_dir: Path) -> list[str]:
    """Cap.3: Cohort Analysis — 2 JSONs."""
    paths = []

    # 03_cohort_heatmap.json — pivoteia a matriz de retenção
    if "cohort_retencao" in resultados:
        df = resultados["cohort_retencao"]
        # Converter coorte_mes pra string YYYY-MM
        df = df.copy()
        df["coorte_mes"] = pd.to_datetime(df["coorte_mes"]).dt.strftime("%Y-%m")

        coortes = sorted(df["coorte_mes"].unique().tolist())
        max_periodo = int(df["periodo"].max()) if len(df) > 0 else 0
        periodos = list(range(0, max_periodo + 1))

        dados = []
        for coorte in coortes:
            df_c = df[df["coorte_mes"] == coorte]
            tamanho_row = df_c[df_c["periodo"] == 0]
            tamanho = (
                int(tamanho_row["tamanho_coorte"].iloc[0])
                if len(tamanho_row) > 0
                else 0
            )

            retencao = []
            for p in periodos:
                row = df_c[df_c["periodo"] == p]
                if len(row) > 0:
                    taxa = row["taxa_retencao"].iloc[0]
                    retencao.append(
                        _clean_value(round(float(taxa), 4)) if pd.notna(taxa) else None
                    )
                else:
                    retencao.append(None)

            dados.append(
                {
                    "coorte": coorte,
                    "tamanho": tamanho,
                    "retencao": retencao,
                }
            )

        heatmap = {
            "coortes": coortes,
            "periodos": periodos,
            "dados": dados,
        }
        _save_json(heatmap, output_dir / "03_cohort_heatmap.json")
        paths.append("03_cohort_heatmap.json")

    # 03_cohort_recompra.json
    if "cohort_recompra" in resultados:
        records = _df_to_records(resultados["cohort_recompra"])
        records = _round_fields(records, monetary=["dias_medio_ate_recompra"])
        _save_json(records, output_dir / "03_cohort_recompra.json")
        paths.append("03_cohort_recompra.json")

    return paths


def _export_cap4_geo(resultados: dict, output_dir: Path) -> list[str]:
    """Cap.4: Análise Geográfica — 3 JSONs."""
    paths = []

    # 04_geo_estados.json
    if "geo_estados" in resultados:
        records = _df_to_records(resultados["geo_estados"])
        records = _round_fields(
            records,
            monetary=["receita", "ticket_medio", "frete_medio"],
        )
        _save_json(records, output_dir / "04_geo_estados.json")
        paths.append("04_geo_estados.json")

    # 04_geo_correlacao.json — dados de correlação frete × satisfação
    if "geo_correlacao" in resultados:
        data = resultados["geo_correlacao"]
        # Se for dict (de hipoteses.py), limpar valores
        if isinstance(data, dict):
            data = {k: _clean_value(v) for k, v in data.items()}
        elif isinstance(data, pd.DataFrame):
            data = _df_to_records(data)
        _save_json(data, output_dir / "04_geo_correlacao.json")
        paths.append("04_geo_correlacao.json")

    # 04_geo_categorias.json
    if "geo_categorias" in resultados:
        records = _df_to_records(resultados["geo_categorias"])
        records = _round_fields(records, monetary=["receita"])
        _save_json(records, output_dir / "04_geo_categorias.json")
        paths.append("04_geo_categorias.json")

    return paths


def _export_cap5_sazonalidade(resultados: dict, output_dir: Path) -> list[str]:
    """Cap.5: Sazonalidade — 3 JSONs."""
    paths = []

    # 05_sazonalidade_mensal.json
    if "sazonalidade_mensal" in resultados:
        df = resultados["sazonalidade_mensal"].copy()
        # Converter mes pra string YYYY-MM
        if "mes" in df.columns:
            df["mes"] = pd.to_datetime(df["mes"]).dt.strftime("%Y-%m")
        records = _df_to_records(df)
        records = _round_fields(records, monetary=["receita", "media_movel_3m"])
        _save_json(records, output_dir / "05_sazonalidade_mensal.json")
        paths.append("05_sazonalidade_mensal.json")

    # 05_sazonalidade_semanal.json
    if "sazonalidade_semanal" in resultados:
        records = _df_to_records(resultados["sazonalidade_semanal"])
        records = _round_fields(records, monetary=["receita_media", "ticket_medio"])
        _save_json(records, output_dir / "05_sazonalidade_semanal.json")
        paths.append("05_sazonalidade_semanal.json")

    # 05_sazonalidade_horaria.json
    if "sazonalidade_horaria" in resultados:
        records = _df_to_records(resultados["sazonalidade_horaria"])
        records = _round_fields(records, monetary=["receita"])
        _save_json(records, output_dir / "05_sazonalidade_horaria.json")
        paths.append("05_sazonalidade_horaria.json")

    return paths


def _export_cap6_reviews(resultados: dict, output_dir: Path) -> list[str]:
    """Cap.6: Reviews e Satisfação — 4 JSONs."""
    paths = []

    # 06_reviews_distribuicao.json
    if "reviews_distribuicao" in resultados:
        records = _df_to_records(resultados["reviews_distribuicao"])
        _save_json(records, output_dir / "06_reviews_distribuicao.json")
        paths.append("06_reviews_distribuicao.json")

    # 06_reviews_categorias.json
    if "reviews_categorias" in resultados:
        records = _df_to_records(resultados["reviews_categorias"])
        records = _round_fields(records, monetary=["score_medio"])
        _save_json(records, output_dir / "06_reviews_categorias.json")
        paths.append("06_reviews_categorias.json")

    # 06_reviews_atraso.json
    if "reviews_atraso" in resultados:
        records = _df_to_records(resultados["reviews_atraso"])
        records = _round_fields(records, monetary=["score_medio"])
        _save_json(records, output_dir / "06_reviews_atraso.json")
        paths.append("06_reviews_atraso.json")

    # 06_reviews_palavras.json
    if "reviews_palavras" in resultados:
        data = resultados["reviews_palavras"]
        if isinstance(data, pd.DataFrame):
            data = _df_to_records(data)
        _save_json(data, output_dir / "06_reviews_palavras.json")
        paths.append("06_reviews_palavras.json")

    return paths


# --------------------------------------------------------------------------- #
# Função principal
# --------------------------------------------------------------------------- #


def export_all(
    resultados: dict,
    output_dir: str | Path | None = None,
) -> list[str]:
    """Exporta todos os resultados como JSONs otimizados pro dashboard.

    Args:
        resultados: Dict com DataFrames e dicts de todos os capítulos.
            Chaves esperadas (cada uma opcional):
            - funil_status, funil_conversao, funil_tempos (Cap.1)
            - rfm_scores, rfm_segmentos, clustering (Cap.2)
            - cohort_retencao, cohort_recompra (Cap.3)
            - geo_estados, geo_correlacao, geo_categorias (Cap.4)
            - sazonalidade_mensal, sazonalidade_semanal, sazonalidade_horaria (Cap.5)
            - reviews_distribuicao, reviews_categorias, reviews_atraso,
              reviews_palavras (Cap.6)
        output_dir: Diretório de saída. Se None, usa config padrão.

    Returns:
        Lista de nomes dos JSONs gerados.
    """
    output_path = Path(output_dir) if output_dir else DATA_OUTPUT_DIR
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info("Exportando JSONs para %s", output_path)

    all_paths: list[str] = []

    all_paths.extend(_export_cap1_funil(resultados, output_path))
    all_paths.extend(_export_cap2_rfm(resultados, output_path))
    all_paths.extend(_export_cap3_cohort(resultados, output_path))
    all_paths.extend(_export_cap4_geo(resultados, output_path))
    all_paths.extend(_export_cap5_sazonalidade(resultados, output_path))
    all_paths.extend(_export_cap6_reviews(resultados, output_path))

    logger.info("Export concluído: %d JSONs gerados", len(all_paths))
    return all_paths


def main() -> None:
    """Entrypoint para python -m pipeline.export."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.info("Use 'python -m pipeline.run' para executar o pipeline completo.")


if __name__ == "__main__":
    main()
