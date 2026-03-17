"""Constantes e configurações do pipeline."""

from pathlib import Path

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Diretórios de dados
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_OUTPUT_DIR = DATA_DIR / "output"

# Banco DuckDB
DUCKDB_PATH = DATA_PROCESSED_DIR / "olist.duckdb"

# CSVs esperados do dataset Olist
EXPECTED_CSVS = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]

# Análise
MIN_ORDERS_RFM = 1
REFERENCE_DATE = "2018-09-01"
SIGNIFICANCE_LEVEL = 0.05
RANDOM_STATE = 42
