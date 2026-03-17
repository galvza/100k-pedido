# 100k Pedidos — Raio-X do E-commerce Brasileiro

![CI](https://github.com/galvza/100k-pedidos/actions/workflows/ci.yml/badge.svg)

Pipeline completo de análise de dados — SQL analítico avançado (DuckDB) → Python (estatística e ML) → visualização interativa (Next.js + Recharts) — usando dados reais de 100k pedidos do marketplace brasileiro Olist.

**[Ver dashboard ao vivo →](https://ecommerce.seudominio.com)**

---

## O projeto

Análise exploratória e estatística de ~100 mil pedidos do Olist (2016–2018), organizada em seis capítulos narrativos:

| Capítulo | Análise |
|----------|---------|
| Funil de vendas | Conversão, status e tempo de entrega |
| Segmentação RFM | Recência, Frequência e Valor — K-Means |
| Análise de Cohort | Retenção e recompra por coorte mensal |
| Mapa geográfico | Pedidos e ticket médio por estado |
| Sazonalidade | Padrões mensais, semanais e horários |
| Avaliações | Correlação com atraso, NPS por categoria |

O dataset é público e está disponível no Kaggle: [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Análise SQL | DuckDB 1.1+ |
| Análise Python | Python 3.11+ · pandas · scipy · scikit-learn · statsmodels |
| Visualização Python | matplotlib · seaborn |
| Frontend | Next.js 14 · TypeScript · Recharts · Leaflet · Tailwind CSS |
| Testes | pytest · Vitest |
| Deploy | Cloudflare Pages (static export) |

---

## Como reproduzir localmente

**Pré-requisitos:** Python 3.11+, Node.js 20 LTS, conta no Kaggle (para download do dataset).

### 1. Clone o repositório

```bash
git clone https://github.com/galvza/100k-pedidos.git
cd 100k-pedidos
```

### 2. Configure o ambiente Python

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

### 3. Baixe o dataset

```bash
python scripts/download_dataset.py
```

> O script baixa os 9 CSVs do Olist para `data/raw/`. Você precisa de credenciais do Kaggle em `~/.kaggle/kaggle.json`.

### 4. Execute o pipeline

```bash
python -m pipeline.run
```

Isso importa os CSVs pro DuckDB, roda as queries SQL, executa as análises Python e exporta os JSONs para `data/output/`.

### 5. Build do dashboard

```bash
bash scripts/build.sh
```

Copia os JSONs para `dashboard/public/data/` e gera o export estático em `dashboard/out/`.

### 6. Visualize localmente

```bash
npx serve dashboard/out
```

Abra `http://localhost:3000` no navegador.

---

### Desenvolvimento do dashboard (sem reexecutar o pipeline)

Se os JSONs já estão em `dashboard/public/data/`:

```bash
cd dashboard
npm install
npm run dev   # http://localhost:3000
```

---

## Estrutura do projeto

```
100k-pedidos/
├── data/
│   ├── raw/              # CSVs originais do Olist (gitignored)
│   ├── processed/        # DuckDB database (gitignored)
│   └── output/           # JSONs gerados pelo pipeline (commitados)
├── pipeline/             # Pipeline Python (ingest → queries → analyze → export)
│   ├── queries/          # Queries SQL por capítulo
│   └── analyze/          # Estatística + ML
├── sql/                  # Cópia documentada das queries (showcase)
├── notebooks/            # Análise exploratória em Jupyter
├── dashboard/            # App Next.js (static export)
│   ├── src/app/          # Páginas por capítulo (App Router)
│   ├── src/components/   # Gráficos, layout, UI
│   └── public/data/      # JSONs servidos pelo dashboard
├── tests/                # Testes Python (pytest)
├── scripts/              # build.sh, setup.sh, download_dataset.py
└── .github/workflows/    # CI (lint + testes)
```

---

## Deploy no Cloudflare Pages

### Configuração do projeto

No painel do Cloudflare Pages, configure:

| Configuração | Valor |
|-------------|-------|
| Build command | `bash scripts/build.sh` |
| Build output directory | `dashboard/out` |
| Root directory | `/` (raiz do repositório) |
| NODE_VERSION (env var) | `20` |

> **Atenção:** O `build.sh` requer que `data/output/` tenha os JSONs. Como o pipeline não roda no Cloudflare (os dados do DuckDB são locais), os JSONs devem estar **commitados** em `data/output/` antes do deploy — ou o build command deve ser apenas `cd dashboard && npm run build`, com os JSONs já em `dashboard/public/data/`.

### Recomendação para CI/CD

Commite os JSONs de `data/output/` e `dashboard/public/data/` no repositório. O Cloudflare Pages então só precisa rodar o build do Next.js:

```
Build command: cd dashboard && npm run build
Build output directory: dashboard/out
```

### Configuração de DNS

No painel de DNS da Cloudflare, adicione:

| Tipo | Nome | Conteúdo |
|------|------|----------|
| CNAME | `ecommerce` | `[seu-projeto].pages.dev` |

Acesso via `https://ecommerce.seudominio.com` após propagação.

---

## Créditos

por Gabriel — [LinkedIn](https://linkedin.com) · [GitHub](https://github.com/galvza)

Dataset: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — licença CC BY-NC-SA 4.0.

---

## Licença

MIT — veja [LICENSE](LICENSE) para detalhes.
