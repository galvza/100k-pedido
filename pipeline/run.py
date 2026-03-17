"""Orquestrador do pipeline completo: ingest → queries → analyze → export.

Uso:
    python -m pipeline.run
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import duckdb

from pipeline.analyze.clustering import pipeline_clustering
from pipeline.analyze.predicao import pipeline_predicao
from pipeline.config import DATA_OUTPUT_DIR, DUCKDB_PATH
from pipeline.export import export_all
from pipeline.ingest import ingest_all
from pipeline.queries import run_query

logger = logging.getLogger(__name__)


def _run_queries(con: duckdb.DuckDBPyConnection) -> dict:
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
        logger.info("Executando queries de %s...", sql_file)
        query_results = run_query(sql_file, con=con)
        resultados.update(query_results)

    logger.info("Queries concluídas: %d resultados", len(resultados))
    return resultados


def _run_analyses(resultados: dict, db_path: str) -> dict:
    """Executa análises Python (clustering, predição) e adiciona aos resultados."""

    # Clustering RFM (se rfm_scores disponível)
    if "rfm_scores" in resultados:
        df_rfm = resultados["rfm_scores"]
        colunas_rfm = ["recency", "frequency", "monetary"]
        available = [c for c in colunas_rfm if c in df_rfm.columns]
        if len(available) == 3:
            logger.info("Rodando clustering RFM...")
            clustering = pipeline_clustering(df_rfm, colunas=colunas_rfm)
            resultados["clustering"] = clustering
        else:
            logger.warning("Colunas RFM incompletas, pulando clustering")

    # Predição de atraso
    logger.info("Rodando modelo preditivo de atraso...")
    predicao = pipeline_predicao(db_path)
    resultados["predicao"] = predicao

    return resultados


def run_pipeline(
    db_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> list[str]:
    """Executa o pipeline completo: ingest → queries → analyze → export.

    Args:
        db_path: Caminho do DuckDB. Se None, usa config padrão.
        output_dir: Diretório de saída dos JSONs. Se None, usa config padrão.

    Returns:
        Lista de nomes dos JSONs gerados.
    """
    db_path = Path(db_path) if db_path else DUCKDB_PATH
    output_dir = Path(output_dir) if output_dir else DATA_OUTPUT_DIR

    # 1. Ingestão
    logger.info("=" * 60)
    logger.info("ETAPA 1/4: Ingestão dos CSVs")
    logger.info("=" * 60)
    con = ingest_all(db_path=db_path)

    try:
        # 2. Queries
        logger.info("=" * 60)
        logger.info("ETAPA 2/4: Queries SQL")
        logger.info("=" * 60)
        resultados = _run_queries(con)

        # 3. Análises Python
        logger.info("=" * 60)
        logger.info("ETAPA 3/4: Análises Python")
        logger.info("=" * 60)
        resultados = _run_analyses(resultados, str(db_path))

        # 4. Export
        logger.info("=" * 60)
        logger.info("ETAPA 4/4: Exportação de JSONs")
        logger.info("=" * 60)
        json_files = export_all(resultados, output_dir=output_dir)

    finally:
        con.close()

    logger.info("=" * 60)
    logger.info("Pipeline concluído com sucesso! %d JSONs gerados.", len(json_files))
    logger.info("=" * 60)

    return json_files


def main() -> None:
    """Entrypoint para python -m pipeline.run."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        json_files = run_pipeline()
        for f in json_files:
            print(f"  ✓ {f}")
    except FileNotFoundError as e:
        logger.error("Arquivo não encontrado: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Erro no pipeline: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
