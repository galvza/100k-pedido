#!/usr/bin/env bash
# Setup completo do ambiente: venv + deps Python + download dataset + deps dashboard
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=================================="
echo " Setup do Raio-X E-commerce"
echo "=================================="
echo

# 1. Ambiente virtual Python
echo "[1/4] Criando ambiente virtual Python..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "  .venv criado."
else
    echo "  .venv ja existe. Pulando."
fi

# Ativa venv
if [ -f ".venv/Scripts/activate" ]; then
    # Windows (Git Bash / MSYS)
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# 2. Dependencias Python
echo
echo "[2/4] Instalando dependencias Python..."
pip install -r requirements.txt --quiet
echo "  Dependencias Python instaladas."

# 3. Download dataset
echo
echo "[3/4] Baixando dataset Olist..."
python scripts/download_dataset.py

# 4. Dependencias do dashboard
echo
echo "[4/4] Instalando dependencias do dashboard..."
cd dashboard
npm install --silent
echo "  Dependencias do dashboard instaladas."

cd "$PROJECT_ROOT"
echo
echo "=================================="
echo " Setup concluido!"
echo "=================================="
echo
echo "Proximos passos:"
echo "  source .venv/bin/activate   # ou .venv/Scripts/activate no Windows"
echo "  python -m pipeline.run      # executar pipeline completo"
echo "  cd dashboard && npm run dev # rodar dashboard em dev"
