-- ===========================================
-- Cap. 3: Cohort Analysis
-- Técnicas: CTEs encadeadas, DATE_TRUNC, DATE_DIFF, Window Functions (MIN),
--           self-join implícito via CTE, agregações condicionais
-- Dataset: Olist Brazilian E-Commerce (100k pedidos)
-- ===========================================
--
-- Análise de coorte agrupa clientes pelo mês da primeira compra
-- e mede quantos voltam a comprar nos meses seguintes.
--
-- No contexto de marketplace, a retenção é naturalmente baixa:
-- clientes compram de vendedores diferentes e não têm fidelidade
-- à plataforma. Isso é esperado e documentado — o insight é
-- justamente quantificar essa baixa retenção.
--
-- Usa customer_unique_id (não customer_id) para identificar
-- recompra real. Apenas pedidos 'delivered' são considerados.
--
-- Dois resultados:
--   1. Matriz de retenção (coorte × período em meses)
--   2. Métricas gerais de recompra
-- ===========================================


-- -------------------------------------------------
-- 1. Matriz de retenção por coorte
-- -------------------------------------------------
-- Pipeline de CTEs:
--   1. primeira_compra: identifica a coorte (mês) de cada cliente
--   2. compras_com_coorte: associa cada compra ao período relativo
--   3. cohort_counts: conta clientes ativos por coorte + período
--   4. cohort_sizes: tamanho original de cada coorte (período 0)
--
-- O resultado final tem uma linha por (coorte, período), onde:
--   - período 0 = mês da primeira compra (taxa = 1.0 por definição)
--   - período N = N meses após a primeira compra
--   - taxa_retencao = clientes_ativos / tamanho_coorte

WITH primeira_compra AS (
  -- Identifica o mês da primeira compra de cada cliente
  -- DATE_TRUNC normaliza para o primeiro dia do mês
  SELECT
    c.customer_unique_id,
    DATE_TRUNC('month', MIN(o.order_purchase_timestamp))::DATE AS coorte_mes
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),

compras_com_coorte AS (
  -- Para cada compra, calcula o período relativo à coorte
  -- DATE_DIFF('month', ...) retorna a diferença em meses inteiros
  SELECT
    pc.customer_unique_id,
    pc.coorte_mes,
    DATE_DIFF(
      'month',
      pc.coorte_mes,
      DATE_TRUNC('month', o.order_purchase_timestamp)::DATE
    ) AS periodo
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN primeira_compra pc ON c.customer_unique_id = pc.customer_unique_id
  WHERE o.order_status = 'delivered'
),

cohort_counts AS (
  -- Conta clientes distintos ativos em cada (coorte, período)
  -- DISTINCT é crucial: um cliente pode ter múltiplos pedidos no mesmo mês
  SELECT
    coorte_mes,
    periodo,
    COUNT(DISTINCT customer_unique_id) AS clientes_ativos
  FROM compras_com_coorte
  GROUP BY coorte_mes, periodo
),

cohort_sizes AS (
  -- Tamanho de cada coorte = número de clientes no período 0
  SELECT
    coorte_mes,
    clientes_ativos AS tamanho_coorte
  FROM cohort_counts
  WHERE periodo = 0
)

-- JOIN para calcular a taxa de retenção
SELECT
  cc.coorte_mes,
  cc.periodo,
  cc.clientes_ativos,
  cs.tamanho_coorte,
  ROUND(cc.clientes_ativos * 1.0 / cs.tamanho_coorte, 4) AS taxa_retencao
FROM cohort_counts cc
JOIN cohort_sizes cs ON cc.coorte_mes = cs.coorte_mes
ORDER BY cc.coorte_mes, cc.periodo;


-- -------------------------------------------------
-- 2. Métricas gerais de recompra
-- -------------------------------------------------
-- Complementa o heatmap com números agregados:
--   - Quantos clientes fizeram recompra?
--   - Qual a taxa geral de recompra?
--   - Quanto tempo em média até a segunda compra?
--
-- Técnica: agregação condicional (CASE WHEN dentro de AVG/COUNT)
-- para separar clientes com recompra dos single-purchase.

WITH cliente_pedidos AS (
  SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS total_pedidos,
    MIN(o.order_purchase_timestamp) AS primeira_compra,
    MAX(o.order_purchase_timestamp) AS ultima_compra
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
)
SELECT
  COUNT(*) AS total_clientes,
  COUNT(CASE WHEN total_pedidos > 1 THEN 1 END) AS clientes_recompra,
  ROUND(
    COUNT(CASE WHEN total_pedidos > 1 THEN 1 END) * 100.0 / COUNT(*), 2
  ) AS taxa_recompra_pct,
  ROUND(AVG(total_pedidos), 2) AS media_pedidos_por_cliente,
  ROUND(AVG(
    CASE
      WHEN total_pedidos > 1
      THEN DATE_DIFF('day', primeira_compra, ultima_compra)
    END
  ), 1) AS dias_medio_ate_recompra
FROM cliente_pedidos;
