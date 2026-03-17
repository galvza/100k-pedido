"""Baixa o dataset Olist do Kaggle e salva em data/raw/.

Tenta usar a Kaggle CLI. Se nao estiver disponivel, imprime
instrucoes para download manual.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Resolve paths relativo ao projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"

DATASET_SLUG = "olistbr/brazilian-ecommerce"
KAGGLE_URL = f"https://www.kaggle.com/datasets/{DATASET_SLUG}"

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


def _count_lines(path: Path) -> int:
    """Conta linhas do CSV (incluindo header)."""
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def _try_kaggle_download() -> bool:
    """Tenta baixar via kaggle CLI. Retorna True se conseguiu."""
    if shutil.which("kaggle") is None:
        return False

    print(f"Kaggle CLI encontrada. Baixando dataset {DATASET_SLUG}...")
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [
                "kaggle", "datasets", "download",
                "-d", DATASET_SLUG,
                "-p", str(DATA_RAW_DIR),
                "--unzip",
            ],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao baixar via Kaggle CLI: {e}")
        return False


def _try_unzip_existing() -> bool:
    """Tenta descompactar um zip ja presente em data/raw/."""
    zip_path = DATA_RAW_DIR / "brazilian-ecommerce.zip"
    if not zip_path.exists():
        # Tenta nome alternativo do Kaggle
        zip_path = DATA_RAW_DIR / "archive.zip"
    if not zip_path.exists():
        return False

    print(f"Zip encontrado em {zip_path}. Descompactando...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(DATA_RAW_DIR)
    zip_path.unlink()
    print("Zip descompactado e removido.")
    return True


def _print_manual_instructions() -> None:
    """Imprime instrucoes para download manual."""
    print()
    print("=" * 60)
    print("DOWNLOAD MANUAL NECESSARIO")
    print("=" * 60)
    print()
    print("A Kaggle CLI nao esta instalada ou configurada.")
    print("Siga os passos abaixo:")
    print()
    print(f"  1. Acesse: {KAGGLE_URL}")
    print("  2. Clique em 'Download' (precisa de conta Kaggle)")
    print(f"  3. Descompacte o zip em: {DATA_RAW_DIR}")
    print()
    print("Ou instale a Kaggle CLI:")
    print()
    print("  pip install kaggle")
    print("  # Configure ~/.kaggle/kaggle.json com sua API key")
    print("  # Veja: https://www.kaggle.com/docs/api")
    print("  python scripts/download_dataset.py")
    print()
    print("CSVs esperados:")
    for csv_name in EXPECTED_CSVS:
        print(f"  - {csv_name}")
    print("=" * 60)


def _validate() -> bool:
    """Valida que os 9 CSVs existem e imprime contagem de linhas."""
    print()
    print("Validando CSVs em data/raw/...")
    print()

    all_ok = True
    for csv_name in EXPECTED_CSVS:
        csv_path = DATA_RAW_DIR / csv_name
        if csv_path.exists():
            lines = _count_lines(csv_path)
            size_mb = csv_path.stat().st_size / (1024 * 1024)
            print(f"  OK  {csv_name}: {lines:>10,} linhas  ({size_mb:.1f} MB)")
        else:
            print(f"  FALTA  {csv_name}")
            all_ok = False

    print()
    if all_ok:
        print(f"Todos os 9 CSVs presentes em {DATA_RAW_DIR}")
    else:
        print("ERRO: CSVs faltando. Verifique o download.")
    return all_ok


def main() -> None:
    """Fluxo principal de download."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Se os CSVs ja existem, so validar
    existing = [f for f in EXPECTED_CSVS if (DATA_RAW_DIR / f).exists()]
    if len(existing) == len(EXPECTED_CSVS):
        print("Todos os CSVs ja existem em data/raw/. Pulando download.")
        _validate()
        return

    # Tenta descompactar zip existente
    if _try_unzip_existing():
        _validate()
        return

    # Tenta Kaggle CLI
    if _try_kaggle_download():
        _validate()
        return

    # Fallback: instrucoes manuais
    _print_manual_instructions()
    sys.exit(1)


if __name__ == "__main__":
    main()
