"""Fixtures compartilhadas para testes do pipeline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import duckdb
import pandas as pd
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Mapeamento: nome lógico → arquivo CSV → nome da tabela no DuckDB
TABLES = {
    "customers": {
        "csv": "olist_customers_dataset.csv",
        "columns": {
            "customer_id": "VARCHAR",
            "customer_unique_id": "VARCHAR",
            "customer_zip_code_prefix": "VARCHAR",
            "customer_city": "VARCHAR",
            "customer_state": "VARCHAR",
        },
    },
    "orders": {
        "csv": "olist_orders_dataset.csv",
        "columns": {
            "order_id": "VARCHAR",
            "customer_id": "VARCHAR",
            "order_status": "VARCHAR",
            "order_purchase_timestamp": "TIMESTAMP",
            "order_approved_at": "TIMESTAMP",
            "order_delivered_carrier_date": "TIMESTAMP",
            "order_delivered_customer_date": "TIMESTAMP",
            "order_estimated_delivery_date": "TIMESTAMP",
        },
    },
    "order_items": {
        "csv": "olist_order_items_dataset.csv",
        "columns": {
            "order_id": "VARCHAR",
            "order_item_id": "INTEGER",
            "product_id": "VARCHAR",
            "seller_id": "VARCHAR",
            "shipping_limit_date": "TIMESTAMP",
            "price": "DECIMAL(10,2)",
            "freight_value": "DECIMAL(10,2)",
        },
    },
    "order_payments": {
        "csv": "olist_order_payments_dataset.csv",
        "columns": {
            "order_id": "VARCHAR",
            "payment_sequential": "INTEGER",
            "payment_type": "VARCHAR",
            "payment_installments": "INTEGER",
            "payment_value": "DECIMAL(10,2)",
        },
    },
    "order_reviews": {
        "csv": "olist_order_reviews_dataset.csv",
        "columns": {
            "review_id": "VARCHAR",
            "order_id": "VARCHAR",
            "review_score": "INTEGER",
            "review_comment_title": "VARCHAR",
            "review_comment_message": "VARCHAR",
            "review_creation_date": "TIMESTAMP",
            "review_answer_timestamp": "TIMESTAMP",
        },
    },
    "products": {
        "csv": "olist_products_dataset.csv",
        "columns": {
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
    },
    "sellers": {
        "csv": "olist_sellers_dataset.csv",
        "columns": {
            "seller_id": "VARCHAR",
            "seller_zip_code_prefix": "VARCHAR",
            "seller_city": "VARCHAR",
            "seller_state": "VARCHAR",
        },
    },
    "geolocation": {
        "csv": "olist_geolocation_dataset.csv",
        "columns": {
            "geolocation_zip_code_prefix": "VARCHAR",
            "geolocation_lat": "DOUBLE",
            "geolocation_lng": "DOUBLE",
            "geolocation_city": "VARCHAR",
            "geolocation_state": "VARCHAR",
        },
    },
    "category_translation": {
        "csv": "product_category_name_translation.csv",
        "columns": {
            "product_category_name": "VARCHAR",
            "product_category_name_english": "VARCHAR",
        },
    },
}


def _load_table(con: duckdb.DuckDBPyConnection, table_name: str, spec: dict) -> None:
    """Cria tabela no DuckDB e importa dados do CSV de fixture."""
    csv_path = FIXTURES_DIR / spec["csv"]
    col_defs = ", ".join(f"{col} {dtype}" for col, dtype in spec["columns"].items())
    con.execute(f"CREATE TABLE {table_name} ({col_defs})")

    col_names = list(spec["columns"].keys())
    col_list = ", ".join(col_names)
    # Usar read_csv_auto do DuckDB com tratamento de valores vazios como NULL
    con.execute(f"""
        INSERT INTO {table_name} ({col_list})
        SELECT {col_list}
        FROM read_csv_auto('{csv_path.as_posix()}', nullstr='')
    """)


@pytest.fixture(scope="session")
def sample_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """DuckDB in-memory populado com todos os CSVs de amostra.

    Scope session pra evitar recriar o banco a cada teste.
    """
    con = duckdb.connect(":memory:")
    for table_name, spec in TABLES.items():
        _load_table(con, table_name, spec)
    yield con
    con.close()


@pytest.fixture(scope="session")
def sample_dataframes(sample_db: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    """Retorna dict com DataFrames pandas de todas as tabelas.

    Chave = nome da tabela, valor = DataFrame.
    """
    dfs = {}
    for table_name in TABLES:
        dfs[table_name] = sample_db.execute(f"SELECT * FROM {table_name}").fetchdf()
    return dfs


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Diretório temporário pra JSONs de teste.

    Cada teste recebe um diretório limpo e isolado.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
