"""Execução de queries SQL no DuckDB.

Cada arquivo .sql pode conter múltiplas queries separadas por ';'.
Queries nomeadas usam o comentário '-- nome: <nome>' na linha anterior.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import duckdb
import pandas as pd

from pipeline.config import DUCKDB_PATH

logger = logging.getLogger(__name__)

QUERIES_DIR = Path(__file__).parent


def _split_queries(sql_text: str) -> list[tuple[str, str]]:
    """Divide arquivo SQL em queries individuais nomeadas.

    Retorna lista de (nome, sql). O nome vem do comentário
    '-- nome: <nome>' que precede cada query.
    """
    # Remove comentários de cabeçalho (linhas que começam com -- mas não são nomes)
    queries: list[tuple[str, str]] = []
    current_name = ""
    current_sql_lines: list[str] = []

    for line in sql_text.split("\n"):
        name_match = re.match(r"^--\s*nome:\s*(\w+)", line.strip())
        if name_match:
            # Salva query anterior se existir
            if current_name and current_sql_lines:
                sql = "\n".join(current_sql_lines).strip().rstrip(";")
                if sql:
                    queries.append((current_name, sql))
            current_name = name_match.group(1)
            current_sql_lines = []
        else:
            current_sql_lines.append(line)

    # Última query
    if current_name and current_sql_lines:
        sql = "\n".join(current_sql_lines).strip().rstrip(";")
        if sql:
            queries.append((current_name, sql))

    return queries


def run_query(
    sql_file: str | Path,
    db_path: str | Path | None = None,
    con: duckdb.DuckDBPyConnection | None = None,
) -> dict[str, pd.DataFrame]:
    """Executa arquivo SQL e retorna DataFrames nomeados.

    Args:
        sql_file: Caminho do arquivo .sql (absoluto ou relativo a queries/).
        db_path: Caminho do DuckDB. Ignorado se con for fornecido.
        con: Conexão DuckDB existente (ex: in-memory pra testes).

    Returns:
        Dict com nome da query → DataFrame pandas.
    """
    sql_path = Path(sql_file)
    if not sql_path.is_absolute():
        sql_path = QUERIES_DIR / sql_path

    sql_text = sql_path.read_text(encoding="utf-8")
    queries = _split_queries(sql_text)

    if not queries:
        raise ValueError(f"Nenhuma query nomeada encontrada em {sql_path}")

    should_close = False
    if con is None:
        db_path = Path(db_path) if db_path else DUCKDB_PATH
        con = duckdb.connect(str(db_path), read_only=True)
        should_close = True

    try:
        results: dict[str, pd.DataFrame] = {}
        for name, sql in queries:
            logger.info("Executando query '%s' de %s", name, sql_path.name)
            df = con.execute(sql).fetchdf()
            results[name] = df
            logger.info("  %s: %d linhas, %d colunas", name, len(df), len(df.columns))
        return results
    finally:
        if should_close:
            con.close()
