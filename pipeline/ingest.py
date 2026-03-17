"""Importa os 9 CSVs do dataset Olist para tabelas no DuckDB.

Uso:
    python -m pipeline.ingest
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from pipeline.config import (
    DATA_PROCESSED_DIR,
    DATA_RAW_DIR,
    DUCKDB_PATH,
    EXPECTED_CSVS,
)

logger = logging.getLogger(__name__)

# Mapeamento: arquivo CSV → (nome da tabela, definição de colunas)
TABLE_SPECS: dict[str, tuple[str, dict[str, str]]] = {
    "olist_customers_dataset.csv": (
        "customers",
        {
            "customer_id": "VARCHAR",
            "customer_unique_id": "VARCHAR",
            "customer_zip_code_prefix": "VARCHAR",
            "customer_city": "VARCHAR",
            "customer_state": "VARCHAR",
        },
    ),
    "olist_orders_dataset.csv": (
        "orders",
        {
            "order_id": "VARCHAR",
            "customer_id": "VARCHAR",
            "order_status": "VARCHAR",
            "order_purchase_timestamp": "TIMESTAMP",
            "order_approved_at": "TIMESTAMP",
            "order_delivered_carrier_date": "TIMESTAMP",
            "order_delivered_customer_date": "TIMESTAMP",
            "order_estimated_delivery_date": "TIMESTAMP",
        },
    ),
    "olist_order_items_dataset.csv": (
        "order_items",
        {
            "order_id": "VARCHAR",
            "order_item_id": "INTEGER",
            "product_id": "VARCHAR",
            "seller_id": "VARCHAR",
            "shipping_limit_date": "TIMESTAMP",
            "price": "DECIMAL(10,2)",
            "freight_value": "DECIMAL(10,2)",
        },
    ),
    "olist_order_payments_dataset.csv": (
        "order_payments",
        {
            "order_id": "VARCHAR",
            "payment_sequential": "INTEGER",
            "payment_type": "VARCHAR",
            "payment_installments": "INTEGER",
            "payment_value": "DECIMAL(10,2)",
        },
    ),
    "olist_order_reviews_dataset.csv": (
        "order_reviews",
        {
            "review_id": "VARCHAR",
            "order_id": "VARCHAR",
            "review_score": "INTEGER",
            "review_comment_title": "VARCHAR",
            "review_comment_message": "VARCHAR",
            "review_creation_date": "TIMESTAMP",
            "review_answer_timestamp": "TIMESTAMP",
        },
    ),
    "olist_products_dataset.csv": (
        "products",
        {
            "product_id": "VARCHAR",
            "product_category_name": "VARCHAR",
            "product_name_length": "INTEGER",
            "product_description_length": "INTEGER",
            "product_photos_qty": "INTEGER",
            "product_weight_g": "INTEGER",
            "product_length_cm": "INTEGER",
            "product_height_cm": "INTEGER",
            "product_width_cm": "INTEGER",
        },
    ),
    "olist_sellers_dataset.csv": (
        "sellers",
        {
            "seller_id": "VARCHAR",
            "seller_zip_code_prefix": "VARCHAR",
            "seller_city": "VARCHAR",
            "seller_state": "VARCHAR",
        },
    ),
    "olist_geolocation_dataset.csv": (
        "geolocation",
        {
            "geolocation_zip_code_prefix": "VARCHAR",
            "geolocation_lat": "DOUBLE",
            "geolocation_lng": "DOUBLE",
            "geolocation_city": "VARCHAR",
            "geolocation_state": "VARCHAR",
        },
    ),
    "product_category_name_translation.csv": (
        "category_translation",
        {
            "product_category_name": "VARCHAR",
            "product_category_name_english": "VARCHAR",
        },
    ),
}

# Contagens esperadas do dataset real (ARCHITECTURE.md)
EXPECTED_ROW_COUNTS: dict[str, int] = {
    "customers": 99_441,
    "orders": 99_441,
    "order_items": 112_650,
    "order_payments": 103_886,
    "order_reviews": 99_224,
    "products": 32_951,
    "sellers": 3_095,
    "geolocation": 1_000_163,
    "category_translation": 71,
}


def _validate_csvs_exist(raw_dir: Path) -> None:
    """Verifica se todos os 9 CSVs existem no diretório."""
    missing = [f for f in EXPECTED_CSVS if not (raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"CSVs faltando em {raw_dir}: {', '.join(missing)}. "
            "Execute: python scripts/download_dataset.py"
        )


def _load_table(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    columns: dict[str, str],
    csv_path: Path,
) -> int:
    """Cria tabela com schema explícito e importa CSV. Retorna contagem de linhas."""
    col_defs = ", ".join(f"{col} {dtype}" for col, dtype in columns.items())
    con.execute(f"CREATE TABLE {table_name} ({col_defs})")

    col_list = ", ".join(columns.keys())
    con.execute(f"""
        INSERT INTO {table_name} ({col_list})
        SELECT {col_list}
        FROM read_csv_auto('{csv_path.as_posix()}', nullstr='')
    """)

    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return row_count


def _check_untranslated_categories(con: duckdb.DuckDBPyConnection) -> None:
    """Loga categorias de produtos sem tradução."""
    result = con.execute("""
        SELECT DISTINCT p.product_category_name
        FROM products p
        LEFT JOIN category_translation ct
            ON p.product_category_name = ct.product_category_name
        WHERE ct.product_category_name IS NULL
          AND p.product_category_name IS NOT NULL
          AND p.product_category_name != ''
    """).fetchall()

    if result:
        categories = [row[0] for row in result]
        logger.warning(
            "Categorias sem traducao (%d): %s",
            len(categories),
            ", ".join(categories),
        )
    else:
        logger.info("Todas as categorias possuem traducao.")


def ingest_all(
    db_path: str | Path | None = None,
    raw_dir: str | Path | None = None,
) -> duckdb.DuckDBPyConnection:
    """Importa todos os CSVs do Olist para DuckDB.

    Args:
        db_path: Caminho do arquivo DuckDB. Se None, usa config padrão.
        raw_dir: Diretório dos CSVs. Se None, usa config padrão.

    Returns:
        Conexão DuckDB aberta com todas as tabelas carregadas.
    """
    db_path = Path(db_path) if db_path else DUCKDB_PATH
    raw_dir = Path(raw_dir) if raw_dir else DATA_RAW_DIR

    _validate_csvs_exist(raw_dir)

    # Remove banco existente pra garantir estado limpo
    if db_path.exists():
        logger.info("Removendo banco existente: %s", db_path)
        db_path.unlink()

    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Criando banco DuckDB: %s", db_path)
    con = duckdb.connect(str(db_path))

    total_rows = 0
    for csv_file, (table_name, columns) in TABLE_SPECS.items():
        csv_path = raw_dir / csv_file
        logger.info("Importando %s -> tabela %s...", csv_file, table_name)

        row_count = _load_table(con, table_name, columns, csv_path)
        total_rows += row_count

        # Validar contagem vs esperado
        expected = EXPECTED_ROW_COUNTS.get(table_name)
        if expected and abs(row_count - expected) / expected > 0.01:
            logger.warning(
                "  %s: %d linhas (esperado ~%d, diferenca de %.1f%%)",
                table_name,
                row_count,
                expected,
                abs(row_count - expected) / expected * 100,
            )
        else:
            logger.info("  %s: %d linhas OK", table_name, row_count)

    _check_untranslated_categories(con)

    logger.info(
        "Ingestao concluida: 9 tabelas, %d linhas totais em %s",
        total_rows,
        db_path,
    )
    return con


def main() -> None:
    """Entrypoint para python -m pipeline.ingest."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    con = ingest_all()
    con.close()


if __name__ == "__main__":
    main()
