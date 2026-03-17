-- Analise Geografica: metricas por estado, vendedores, top categorias

-- Resultado 1: metricas agregadas por UF do cliente
-- nome: geo_estados
WITH pedidos_estado AS (
  SELECT
    c.customer_state AS estado,
    o.order_id,
    oi.price,
    oi.freight_value,
    r.review_score
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN order_items oi ON o.order_id = oi.order_id
  LEFT JOIN order_reviews r ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
),
vendedores_estado AS (
  SELECT
    seller_state AS estado,
    COUNT(*) AS total_vendedores
  FROM sellers
  GROUP BY seller_state
)
SELECT
  pe.estado,
  COUNT(DISTINCT pe.order_id) AS pedidos,
  ROUND(CAST(SUM(pe.price + pe.freight_value) AS NUMERIC), 2) AS receita,
  ROUND(CAST(SUM(pe.price + pe.freight_value) / COUNT(DISTINCT pe.order_id) AS NUMERIC), 2) AS ticket_medio,
  ROUND(CAST(AVG(pe.freight_value) AS NUMERIC), 2) AS frete_medio,
  ROUND(CAST(AVG(pe.freight_value / NULLIF(pe.price + pe.freight_value, 0)) AS NUMERIC), 4) AS frete_percentual,
  ROUND(AVG(pe.review_score), 2) AS review_score_medio,
  COALESCE(ve.total_vendedores, 0) AS total_vendedores
FROM pedidos_estado pe
LEFT JOIN vendedores_estado ve ON pe.estado = ve.estado
GROUP BY pe.estado, ve.total_vendedores
ORDER BY pedidos DESC;

-- Resultado 2: top 3 categorias por UF
-- nome: geo_categorias
WITH pedidos_categoria AS (
  SELECT
    c.customer_state AS estado,
    COALESCE(ct.product_category_name_english, p.product_category_name, 'sem_categoria') AS categoria,
    COUNT(DISTINCT o.order_id) AS pedidos,
    ROUND(CAST(SUM(oi.price) AS NUMERIC), 2) AS receita
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN order_items oi ON o.order_id = oi.order_id
  JOIN products p ON oi.product_id = p.product_id
  LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_state, COALESCE(ct.product_category_name_english, p.product_category_name, 'sem_categoria')
),
ranked AS (
  SELECT
    estado,
    categoria,
    pedidos,
    receita,
    ROW_NUMBER() OVER (PARTITION BY estado ORDER BY pedidos DESC, receita DESC) AS rank
  FROM pedidos_categoria
)
SELECT estado, categoria, pedidos, receita
FROM ranked
WHERE rank <= 3
ORDER BY estado, rank;
