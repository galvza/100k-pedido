#!/usr/bin/env bash
# Build script para deploy no Cloudflare Pages
# Copia os JSONs do pipeline para o dashboard e gera o static export
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_OUTPUT="$PROJECT_ROOT/data/output"
DATA_PUBLIC="$PROJECT_ROOT/dashboard/public/data"
DASHBOARD_DIR="$PROJECT_ROOT/dashboard"

echo "=================================="
echo " Build — 100k Pedidos"
echo "=================================="
echo

# 1. Verificar que data/output/ existe e não está vazio
echo "[1/3] Verificando dados do pipeline..."
if [ ! -d "$DATA_OUTPUT" ]; then
    echo "ERRO: Diretório data/output/ não encontrado."
    echo "  Execute o pipeline primeiro: python -m pipeline.run"
    exit 1
fi

JSON_COUNT=$(find "$DATA_OUTPUT" -maxdepth 1 -name "*.json" | wc -l)
if [ "$JSON_COUNT" -eq 0 ]; then
    echo "ERRO: Nenhum JSON encontrado em data/output/."
    echo "  Execute o pipeline primeiro: python -m pipeline.run"
    exit 1
fi

echo "  $JSON_COUNT JSONs encontrados em data/output/."

# 2. Copiar JSONs para dashboard/public/data/
echo
echo "[2/3] Copiando JSONs para dashboard/public/data/..."
mkdir -p "$DATA_PUBLIC"
cp "$DATA_OUTPUT"/*.json "$DATA_PUBLIC/"
echo "  JSONs copiados com sucesso."

# 3. Build do Next.js (static export)
echo
echo "[3/3] Gerando build estático do dashboard..."
cd "$DASHBOARD_DIR"
npm run build
echo "  Build concluído em dashboard/out/."

echo
echo "=================================="
echo " Build finalizado!"
echo "=================================="
echo
echo "Para visualizar localmente:"
echo "  npx serve dashboard/out"
