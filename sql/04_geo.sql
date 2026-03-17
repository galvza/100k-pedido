-- ===========================================
-- Cap. 4: Análise Geográfica
-- Técnicas: JOINs multi-tabela (5 tabelas), agregações por UF,
--           COALESCE, NULLIF, ROW_NUMBER, subquery/CTE para vendedores
-- Dataset: Olist Brazilian E-Commerce (100k pedidos)
-- ===========================================
--
-- Agrega métricas de pedidos, receita, frete e satisfação por
-- estado brasileiro (UF do cliente). Também identifica a
-- concentração de vendedores vs clientes e as top categorias
-- de produto por estado.
--
-- JOINs envolvidos:
--   orders → customers (customer_state)
--   orders → order_items (price, freight_value)
--   orders → order_reviews (review_score)
--   order_items → products → category_translation (categoria)
--   sellers (agregação separada por seller_state)
--
-- Apenas pedidos 'delivered' são considerados para evitar
-- distorção nas métricas de satisfação e entrega.
-- ===========================================


-- -------------------------------------------------
-- 1. Métricas agregadas por estado
-- -------------------------------------------------
-- Cada linha = 1 UF com métricas consolidadas.
-- frete_percentual = frete / (price + freight) médio por item,
-- representando o peso do frete no valor total.
--
-- Vendedores são contados separadamente (CTE vendedores_estado)
-- e joinados via LEFT JOIN — estados sem vendedores recebem 0.

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
  -- Contagem de vendedores cadastrados por estado
  -- Independente de pedidos — um estado pode ter vendedores
  -- mesmo sem clientes comprando daquele estado
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
  ROUND(CAST(
    SUM(pe.price + pe.freight_value) / COUNT(DISTINCT pe.order_id)
  AS NUMERIC), 2) AS ticket_medio,
  ROUND(CAST(AVG(pe.freight_value) AS NUMERIC), 2) AS frete_medio,
  -- NULLIF evita divisão por zero em itens com preço 0
  ROUND(CAST(
    AVG(pe.freight_value / NULLIF(pe.price + pe.freight_value, 0))
  AS NUMERIC), 4) AS frete_percentual,
  ROUND(AVG(pe.review_score), 2) AS review_score_medio,
  COALESCE(ve.total_vendedores, 0) AS total_vendedores
FROM pedidos_estado pe
LEFT JOIN vendedores_estado ve ON pe.estado = ve.estado
GROUP BY pe.estado, ve.total_vendedores
ORDER BY pedidos DESC;


-- -------------------------------------------------
-- 2. Top 3 categorias por estado
-- -------------------------------------------------
-- Para cada UF, identifica as 3 categorias de produto com
-- mais pedidos. Usa ROW_NUMBER() OVER (PARTITION BY estado)
-- para rankear dentro de cada estado.
--
-- COALESCE trata categorias sem tradução e produtos sem
-- categoria, atribuindo 'sem_categoria' como fallback.

WITH pedidos_categoria AS (
  SELECT
    c.customer_state AS estado,
    COALESCE(
      ct.product_category_name_english,
      p.product_category_name,
      'sem_categoria'
    ) AS categoria,
    COUNT(DISTINCT o.order_id) AS pedidos,
    ROUND(CAST(SUM(oi.price) AS NUMERIC), 2) AS receita
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN order_items oi ON o.order_id = oi.order_id
  JOIN products p ON oi.product_id = p.product_id
  LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
  WHERE o.order_status = 'delivered'
  GROUP BY
    c.customer_state,
    COALESCE(ct.product_category_name_english, p.product_category_name, 'sem_categoria')
),
ranked AS (
  -- ROW_NUMBER garante exatamente 1 rank por linha (sem empates)
  -- Desempate por receita caso pedidos sejam iguais
  SELECT
    estado,
    categoria,
    pedidos,
    receita,
    ROW_NUMBER() OVER (
      PARTITION BY estado
      ORDER BY pedidos DESC, receita DESC
    ) AS rank
  FROM pedidos_categoria
)
SELECT estado, categoria, pedidos, receita
FROM ranked
WHERE rank <= 3
ORDER BY estado, rank;
