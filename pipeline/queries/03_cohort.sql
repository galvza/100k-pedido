-- Cohort Analysis: retencao por coorte de primeira compra

-- Resultado 1: matriz de retencao (coorte x periodo)
-- nome: cohort_retencao
WITH primeira_compra AS (
  SELECT
    c.customer_unique_id,
    DATE_TRUNC('month', MIN(o.order_purchase_timestamp))::DATE AS coorte_mes
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),
compras_com_coorte AS (
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
  SELECT
    coorte_mes,
    periodo,
    COUNT(DISTINCT customer_unique_id) AS clientes_ativos
  FROM compras_com_coorte
  GROUP BY coorte_mes, periodo
),
cohort_sizes AS (
  SELECT
    coorte_mes,
    clientes_ativos AS tamanho_coorte
  FROM cohort_counts
  WHERE periodo = 0
)
SELECT
  cc.coorte_mes,
  cc.periodo,
  cc.clientes_ativos,
  cs.tamanho_coorte,
  ROUND(cc.clientes_ativos * 1.0 / cs.tamanho_coorte, 4) AS taxa_retencao
FROM cohort_counts cc
JOIN cohort_sizes cs ON cc.coorte_mes = cs.coorte_mes
ORDER BY cc.coorte_mes, cc.periodo;

-- Resultado 2: metricas gerais de recompra
-- nome: cohort_recompra
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
