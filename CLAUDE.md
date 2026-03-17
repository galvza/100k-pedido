# CLAUDE.md

## Sobre este projeto

Dashboard interativo de portfólio que demonstra o pipeline completo de análise de dados — SQL analítico avançado (DuckDB) → Python (estatística e ML) → visualização interativa (Next.js + Recharts) — usando dados reais de 100k pedidos do marketplace brasileiro Olist.

---

## Stack

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Análise SQL | DuckDB | 1.1+ |
| Análise Python | Python | 3.11+ |
| Data processing | pandas | 2.2+ |
| Estatística | scipy | 1.13+ |
| Machine Learning | scikit-learn | 1.5+ |
| Visualização Python | matplotlib / seaborn | 3.9+ / 0.13+ |
| Runtime frontend | Node.js | 20 LTS |
| Framework frontend | Next.js | 14.x |
| Linguagem frontend | TypeScript | 5.3+ |
| Visualização frontend | Recharts | 2.12+ |
| Estilização | Tailwind CSS | 3.4+ |
| Testes Python | pytest | 8.x |
| Testes frontend | Vitest | 1.x |
| Gerenciador pacotes Python | pip (com venv) | — |
| Gerenciador pacotes JS | npm | 10+ |

---

## Comandos essenciais

```bash
# ============================================
# PIPELINE PYTHON (rodar da raiz do projeto)
# ============================================

# Criar e ativar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependências Python
pip install -r requirements.txt

# Executar pipeline completo (importa CSVs → DuckDB → queries → análises → JSONs)
python -m pipeline.run

# Executar só a importação dos CSVs pro DuckDB
python -m pipeline.ingest

# Executar só as queries SQL (gera resultados intermediários)
python -m pipeline.queries

# Executar só as análises Python (estatística + ML)
python -m pipeline.analyze

# Executar só a geração de JSONs pro dashboard
python -m pipeline.export

# Rodar testes Python
pytest

# Rodar testes Python com cobertura
pytest --cov=pipeline --cov-report=term-missing

# ============================================
# DASHBOARD NEXT.JS (rodar de /dashboard)
# ============================================

# Instalar dependências
cd dashboard && npm install

# Rodar em desenvolvimento
npm run dev

# Build de produção (static export)
npm run build

# Rodar testes frontend
npm test

# Lint
npm run lint

# Verificação de tipos
npm run typecheck
```

---

## Estrutura de pastas

```
raio-x-ecommerce/
├── data/
│   ├── raw/                    # CSVs originais do Olist (gitignored, baixados via script)
│   ├── processed/              # DuckDB database file (gitignored)
│   └── output/                 # JSONs gerados pro dashboard (commitados)
│
├── pipeline/
│   ├── __init__.py
│   ├── run.py                  # Orquestrador: roda todo o pipeline em sequência
│   ├── ingest.py               # Importa CSVs para DuckDB
│   ├── queries/                # Queries SQL organizadas por capítulo
│   │   ├── __init__.py
│   │   ├── 01_funil.sql
│   │   ├── 02_rfm.sql
│   │   ├── 03_cohort.sql
│   │   ├── 04_geo.sql
│   │   ├── 05_sazonalidade.sql
│   │   └── 06_reviews.sql
│   ├── analyze/                # Análises Python (estatística + ML)
│   │   ├── __init__.py
│   │   ├── descritiva.py       # Estatística descritiva e outliers
│   │   ├── hipoteses.py        # Testes de hipótese
│   │   ├── clustering.py       # K-Means sobre RFM
│   │   ├── predicao.py         # Modelo preditivo de atraso
│   │   └── utils.py            # Funções auxiliares compartilhadas
│   ├── export.py               # Converte resultados em JSONs pro dashboard
│   └── config.py               # Constantes e configurações do pipeline
│
├── sql/                        # Cópia documentada das queries (pra showcase no repo)
│   ├── README.md               # Índice e explicação de cada query
│   ├── 01_funil.sql
│   ├── 02_rfm.sql
│   ├── 03_cohort.sql
│   ├── 04_geo.sql
│   ├── 05_sazonalidade.sql
│   └── 06_reviews.sql
│
├── notebooks/                  # Notebooks exploratórios (documentação da análise)
│   ├── 01_exploracao_inicial.ipynb
│   ├── 02_analise_estatistica.ipynb
│   └── 03_modelagem_ml.ipynb
│
├── dashboard/                  # Projeto Next.js
│   ├── src/
│   │   ├── app/                # App Router (Next.js 14)
│   │   │   ├── layout.tsx      # Layout raiz
│   │   │   ├── page.tsx        # Landing / visão geral
│   │   │   ├── funil/
│   │   │   │   └── page.tsx
│   │   │   ├── rfm/
│   │   │   │   └── page.tsx
│   │   │   ├── cohort/
│   │   │   │   └── page.tsx
│   │   │   ├── geografico/
│   │   │   │   └── page.tsx
│   │   │   ├── sazonalidade/
│   │   │   │   └── page.tsx
│   │   │   └── reviews/
│   │   │       └── page.tsx
│   │   ├── components/         # Componentes React reutilizáveis
│   │   │   ├── charts/         # Wrappers de gráficos Recharts
│   │   │   ├── layout/         # Header, Footer, Navigation, ChapterLayout
│   │   │   ├── ui/             # Componentes genéricos (Card, Badge, Tooltip)
│   │   │   └── editorial/      # Componentes de texto editorial (Insight, Callout)
│   │   ├── lib/                # Utilitários e helpers
│   │   │   ├── data.ts         # Funções pra carregar e processar JSONs
│   │   │   ├── formatters.ts   # Formatação BRL, datas, percentuais
│   │   │   └── constants.ts    # Cores, labels, configurações de gráficos
│   │   └── types/              # Tipos TypeScript
│   │       └── index.ts
│   ├── public/
│   │   └── data/               # Symlink ou cópia dos JSONs de data/output/
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   └── package.json
│
├── tests/
│   ├── pipeline/               # Testes do pipeline Python
│   │   ├── test_ingest.py
│   │   ├── test_queries.py
│   │   ├── test_analyze.py
│   │   └── test_export.py
│   └── conftest.py             # Fixtures compartilhadas (DuckDB in-memory, sample data)
│
├── scripts/
│   ├── download_dataset.py     # Baixa o dataset do Kaggle via API ou URL direta
│   └── setup.sh                # Setup completo do ambiente (venv + deps + download)
│
├── .github/
│   └── workflows/
│       └── ci.yml              # Lint + testes no push
│
├── requirements.txt            # Dependências Python
├── .gitignore
├── CLAUDE.md                   # Este arquivo
├── ARCHITECTURE.md             # Documentação de arquitetura
└── README.md                   # Documentação pública do projeto
```

---

## Convenções de código

### Nomenclatura

| Elemento | Padrão | Exemplo |
|----------|--------|---------|
| Arquivos Python | snake_case | `analise_rfm.py` |
| Funções Python | snake_case | `calcular_rfm_scores()` |
| Classes Python | PascalCase | `PipelineConfig` |
| Constantes Python | UPPER_SNAKE_CASE | `DATA_DIR`, `MIN_ORDERS` |
| Arquivos SQL | snake_case com prefixo numérico | `01_funil.sql` |
| Componentes React | PascalCase | `FunnelChart.tsx` |
| Utilitários TS | camelCase | `formatCurrency.ts` |
| Variáveis/funções TS | camelCase | `getChapterData()` |
| Constantes TS | UPPER_SNAKE_CASE | `CHART_COLORS` |
| Tipos/Interfaces TS | PascalCase sem prefixo | `FunnelData`, `RfmSegment` |
| Rotas Next.js | kebab-case (pasta) | `app/funil/page.tsx` |
| Arquivos JSON de dados | snake_case com prefixo | `01_funil_conversao.json` |

### Estilo Python

- Docstrings em todas as funções públicas (formato Google style)
- Type hints obrigatórios em todas as funções
- Máximo 88 caracteres por linha (Black formatter)
- Imports organizados: stdlib → third-party → local (isort)
- Comentários em português nos queries SQL
- Mensagens de log em português

### Estilo TypeScript

- Arrow functions pra componentes: `const Component = () => {}`
- Preferir `const` sobre `let`. Nunca usar `var`.
- Funções com mais de 30 linhas devem ser divididas
- Imports organizados: libs externas → componentes → utils → tipos
- JSDoc em funções públicas de `lib/`
- Mensagens e textos da interface em português (PT-BR)

### Estilo SQL

- Keywords em UPPERCASE: `SELECT`, `FROM`, `WHERE`, `JOIN`
- Nomes de tabelas e colunas em snake_case (conforme dataset)
- CTEs nomeadas de forma descritiva: `WITH pedidos_entregues AS (...)`
- Cada query tem cabeçalho com: título, descrição, capítulo, técnicas SQL usadas
- Indentação de 2 espaços

### Git

```
tipo(escopo): descrição curta em português

Tipos: feat, fix, refactor, test, docs, chore, data
Escopo: pipeline, dashboard, sql, análise, deploy

Exemplos:
feat(pipeline): implementar importação dos CSVs pro DuckDB
feat(sql): criar query de análise RFM com window functions
feat(dashboard): adicionar capítulo de funil de vendas
data(export): atualizar JSONs com nova análise de cohort
fix(dashboard): corrigir formatação BRL no tooltip
test(pipeline): adicionar testes de validação das queries
docs(sql): documentar query de sazonalidade
```

---

## Variáveis de ambiente

```env
# Não há variáveis de ambiente sensíveis neste projeto.
# O dataset é público e o site é estático.
# Este arquivo existe apenas pra documentação.

# Pipeline
DATA_RAW_DIR=data/raw
DATA_PROCESSED_DIR=data/processed
DATA_OUTPUT_DIR=data/output
DUCKDB_PATH=data/processed/olist.duckdb

# Dashboard
NEXT_PUBLIC_BASE_PATH=                # Vazio em dev, pode ser configurado pra produção
```

---

## Regras do Claude Code

### DEVE fazer
- Rodar testes após cada mudança significativa
- Seguir a estrutura de pastas definida acima
- Comentar queries SQL com descrição e técnicas usadas
- Declarar type hints em todas as funções Python
- Documentar premissas estatísticas (nível de significância, pressupostos)
- Usar formatação brasileira no dashboard (R$, dd/mm/aaaa)
- Manter queries SQL legíveis e bem indentadas (são artefato de portfólio)
- Gerar JSONs otimizados (sem campos desnecessários, valores arredondados)
- Commitar com mensagens no padrão definido

### NÃO deve fazer
- Modificar os CSVs originais do dataset — trabalhar sempre com cópias no DuckDB
- Instalar dependências fora da lista aprovada sem autorização
- Usar `any` como tipo no TypeScript sem justificativa
- Remover outliers silenciosamente — sempre documentar e justificar
- Apresentar resultados de ML sem métricas de validação
- Gerar gráficos com eixo Y que não começa em zero (exceto quando justificado)
- Fazer deploy sem todos os testes passando
- Usar inglês nos textos da interface (dashboard é PT-BR)
- Criar visualizações com gradientes, sombras ou efeitos decorativos

### Quando travar
Se encontrar um problema que não consegue resolver em 3 tentativas:
1. Parar
2. Descrever o problema claramente
3. Listar o que já tentou
4. Pedir orientação

---

## Dependências aprovadas

### Python — Produção

| Pacote | Versão | Pra quê |
|--------|--------|---------|
| duckdb | 1.1+ | Banco analítico SQL |
| pandas | 2.2+ | Manipulação de dataframes |
| numpy | 1.26+ | Operações numéricas |
| scipy | 1.13+ | Testes estatísticos |
| scikit-learn | 1.5+ | Clustering (K-Means) e modelo preditivo |
| statsmodels | 0.14+ | Decomposição sazonal (trend + seasonal + residual) |
| matplotlib | 3.9+ | Gráficos nos notebooks |
| seaborn | 0.13+ | Gráficos estatísticos nos notebooks |

### Python — Desenvolvimento

| Pacote | Versão | Pra quê |
|--------|--------|---------|
| pytest | 8.x | Testes |
| pytest-cov | 5.x | Cobertura de testes |
| black | 24.x | Formatação de código |
| isort | 5.x | Organização de imports |
| jupyterlab | 4.x | Notebooks exploratórios |

### JavaScript — Produção

| Pacote | Versão | Pra quê |
|--------|--------|---------|
| next | 14.x | Framework React com SSG |
| react | 18.x | Biblioteca de UI |
| react-dom | 18.x | Renderização DOM |
| recharts | 2.12+ | Gráficos interativos |
| leaflet | 1.9+ | Mapas interativos |
| react-leaflet | 4.2+ | Wrapper React pro Leaflet |
| tailwindcss | 3.4+ | Estilização utility-first |
| date-fns | 3.x | Formatação de datas |

### JavaScript — Desenvolvimento

| Pacote | Versão | Pra quê |
|--------|--------|---------|
| typescript | 5.3+ | Tipagem estática |
| vitest | 1.x | Testes |
| eslint | 8.x | Lint |
| @types/react | latest | Tipos do React |

---

## Contexto adicional

- **Dataset:** Olist Brazilian E-Commerce (Kaggle) — 9 CSVs, ~100k pedidos, 2016-2018
- **Referência do dataset:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **Projeto irmão:** "O Custo de Vida do Brasileiro" — mesmo padrão de qualidade, mesma stack de dashboard
- **Design:** Editorial, inspirado em Our World in Data e Nexo Jornal. Sem gradientes, sem sombras, serif no texto lead, estrutura por capítulos narrativos
- **Mobile-first:** Responsividade é requisito não-negociável
- **Detalhes técnicos:** Ver ARCHITECTURE.md pra fluxo de dados, modelo de dados, e decisões técnicas
