# Queries SQL — Raio-X do E-commerce Brasileiro

Queries analíticas executadas sobre o dataset Olist (100k pedidos, DuckDB).
Cada arquivo corresponde a um capítulo do dashboard.

## Índice

| # | Arquivo | Capítulo | Técnicas SQL |
|---|---------|----------|-------------|
| 01 | [01_funil.sql](01_funil.sql) | Funil de Vendas | CTE, CASE WHEN, agregações condicionais, DATE_DIFF, UNION ALL |
| 02 | 02_rfm.sql | Segmentação RFM | Window Functions (NTILE), agregações por customer_unique_id |
| 03 | 03_cohort.sql | Análise de Coorte | CTEs encadeadas, MIN (primeira compra), DENSE_RANK |
| 04 | 04_geo.sql | Análise Geográfica | JOINs multi-tabela, agregações por UF, subqueries |
| 05 | 05_sazonalidade.sql | Sazonalidade | DATE_TRUNC, EXTRACT, média móvel com Window Functions |
| 06 | 06_reviews.sql | Reviews e Satisfação | JOINs com aggregation, CASE WHEN, string functions |

## Sobre

Estas são as versões documentadas das queries. As versões de execução ficam em `pipeline/queries/`.
O banco utilizado é o DuckDB (sintaxe muito próxima de PostgreSQL).
