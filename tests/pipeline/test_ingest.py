"""Testes do pipeline de ingestão CSV → DuckDB (T001-T010)."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from pipeline.ingest import TABLE_SPECS, ingest_all

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

EXPECTED_TABLES = {
    "customers",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "products",
    "sellers",
    "geolocation",
    "category_translation",
}

EXPECTED_ROW_COUNTS = {
    "customers": 200,
    "orders": 200,
    "order_items": 200,
    "order_payments": 200,
    "order_reviews": 200,
    "products": 100,
    "sellers": 30,
    "geolocation": 500,
    "category_translation": 71,
}

TIMESTAMP_COLUMNS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}


@pytest.fixture
def ingested_db(tmp_path: Path) -> duckdb.DuckDBPyConnection:
    """Executa ingestão completa com fixtures e retorna conexão."""
    db_path = tmp_path / "test.duckdb"
    con = ingest_all(db_path=db_path, raw_dir=FIXTURES_DIR)
    yield con
    con.close()


# T001 — Criação do banco
class TestDatabaseCreation:
    def test_creates_duckdb_file(self, tmp_path: Path) -> None:
        """T001: ingest_all cria arquivo DuckDB no caminho especificado."""
        db_path = tmp_path / "test.duckdb"
        con = ingest_all(db_path=db_path, raw_dir=FIXTURES_DIR)
        con.close()
        assert db_path.exists()

    def test_recreates_if_exists(self, tmp_path: Path) -> None:
        """T002: Rodar duas vezes não duplica dados — recria o banco."""
        db_path = tmp_path / "test.duckdb"

        con1 = ingest_all(db_path=db_path, raw_dir=FIXTURES_DIR)
        count1 = con1.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        con1.close()

        con2 = ingest_all(db_path=db_path, raw_dir=FIXTURES_DIR)
        count2 = con2.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        con2.close()

        assert count1 == count2


# T003 — Tabelas criadas
class TestTableCreation:
    def test_all_nine_tables_exist(self, ingested_db: duckdb.DuckDBPyConnection) -> None:
        """T003: DuckDB contém exatamente as 9 tabelas esperadas."""
        result = ingested_db.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        tables = {row[0] for row in result}
        assert tables == EXPECTED_TABLES

    def test_table_names_match_spec(self, ingested_db: duckdb.DuckDBPyConnection) -> None:
        """T004: Nomes das tabelas seguem convenção (sem prefixo olist_, sem _dataset)."""
        result = ingested_db.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        tables = {row[0] for row in result}
        for table in tables:
            assert not table.startswith("olist_"), f"Tabela {table} tem prefixo olist_"
            assert not table.endswith("_dataset"), f"Tabela {table} tem sufixo _dataset"


# T005 — Contagem de linhas
class TestRowCounts:
    def test_row_counts_match_fixtures(self, ingested_db: duckdb.DuckDBPyConnection) -> None:
        """T005: Contagem de linhas confere com CSVs de fixture."""
        for table_name, expected in EXPECTED_ROW_COUNTS.items():
            actual = ingested_db.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            assert actual == expected, (
                f"Tabela {table_name}: esperado {expected}, obteve {actual}"
            )


# T006 — Tipos de colunas
class TestColumnTypes:
    def test_timestamp_columns_are_timestamp(
        self, ingested_db: duckdb.DuckDBPyConnection
    ) -> None:
        """T006: Colunas de data são do tipo TIMESTAMP."""
        for table_name, columns in TIMESTAMP_COLUMNS.items():
            result = ingested_db.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                  AND column_name IN ({', '.join(f"'{c}'" for c in columns)})
            """).fetchall()
            col_types = {row[0]: row[1] for row in result}
            for col in columns:
                assert col in col_types, f"Coluna {col} não encontrada em {table_name}"
                assert col_types[col] == "TIMESTAMP", (
                    f"{table_name}.{col}: esperado TIMESTAMP, obteve {col_types[col]}"
                )

    def test_varchar_columns_are_varchar(
        self, ingested_db: duckdb.DuckDBPyConnection
    ) -> None:
        """T007: Colunas de ID e texto são VARCHAR."""
        varchar_checks = [
            ("customers", "customer_id"),
            ("orders", "order_id"),
            ("orders", "order_status"),
            ("products", "product_id"),
            ("sellers", "seller_id"),
            ("geolocation", "geolocation_zip_code_prefix"),
        ]
        for table_name, col_name in varchar_checks:
            result = ingested_db.execute(f"""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}' AND column_name = '{col_name}'
            """).fetchone()
            assert result is not None, f"Coluna {table_name}.{col_name} não encontrada"
            assert result[0] == "VARCHAR", (
                f"{table_name}.{col_name}: esperado VARCHAR, obteve {result[0]}"
            )

    def test_decimal_columns(self, ingested_db: duckdb.DuckDBPyConnection) -> None:
        """T008: Colunas monetárias são DECIMAL."""
        decimal_checks = [
            ("order_items", "price"),
            ("order_items", "freight_value"),
            ("order_payments", "payment_value"),
        ]
        for table_name, col_name in decimal_checks:
            result = ingested_db.execute(f"""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}' AND column_name = '{col_name}'
            """).fetchone()
            assert result is not None
            assert result[0] == "DECIMAL(10,2)", (
                f"{table_name}.{col_name}: esperado DECIMAL(10,2), obteve {result[0]}"
            )


# T009 — Validação de CSVs
class TestInputValidation:
    def test_missing_csv_raises_error(self, tmp_path: Path) -> None:
        """T009: FileNotFoundError se CSVs estiverem faltando."""
        empty_dir = tmp_path / "empty_raw"
        empty_dir.mkdir()
        db_path = tmp_path / "test.duckdb"

        with pytest.raises(FileNotFoundError, match="CSVs faltando"):
            ingest_all(db_path=db_path, raw_dir=empty_dir)


# T010 — Referential integrity post-ingest
class TestReferentialIntegrity:
    def test_orders_reference_valid_customers(
        self, ingested_db: duckdb.DuckDBPyConnection
    ) -> None:
        """T010: Todo customer_id em orders existe em customers."""
        orphans = ingested_db.execute("""
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """).fetchone()[0]
        assert orphans == 0

    def test_order_items_reference_valid_orders(
        self, ingested_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Todo order_id em order_items existe em orders."""
        orphans = ingested_db.execute("""
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """).fetchone()[0]
        assert orphans == 0

    def test_order_items_reference_valid_products(
        self, ingested_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Todo product_id em order_items existe em products."""
        orphans = ingested_db.execute("""
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL
        """).fetchone()[0]
        assert orphans == 0

    def test_order_items_reference_valid_sellers(
        self, ingested_db: duckdb.DuckDBPyConnection
    ) -> None:
        """Todo seller_id em order_items existe em sellers."""
        orphans = ingested_db.execute("""
            SELECT COUNT(*)
            FROM order_items oi
            LEFT JOIN sellers s ON oi.seller_id = s.seller_id
            WHERE s.seller_id IS NULL
        """).fetchone()[0]
        assert orphans == 0
