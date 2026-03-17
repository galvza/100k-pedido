-- ===========================================
-- Cap. 2: RFM Segmentation
-- Técnicas: CTE, Window Functions (NTILE), DATE_DIFF, CASE WHEN, JOINs multi-tabela
-- Dataset: Olist Brazilian E-Commerce (100k pedidos)
-- ===========================================
--
-- RFM é uma técnica clássica de segmentação de clientes:
--   R (Recency)  — dias desde a última compra (menor = melhor)
--   F (Frequency) — número de pedidos (maior = melhor)
--   M (Monetary)  — valor total gasto (maior = melhor)
--
-- Cada dimensão recebe um score de 1 a 5 via NTILE(5).
-- A combinação dos scores define o segmento do cliente.
--
-- NOTA IMPORTANTE: Usamos customer_unique_id (não customer_id)
-- porque customer_id é único por pedido no dataset Olist.
-- customer_unique_id é o identificador real do cliente e
-- permite detectar recompra.
--
-- A data de referência é calculada como MAX(purchase_date) + 1 dia,
-- evitando hardcode e funcionando com qualquer subset do dataset.
-- ===========================================


-- -------------------------------------------------
-- 1. Scores RFM por cliente
-- -------------------------------------------------
-- Pipeline de CTEs:
--   1. data_referencia: calcula data de corte dinamicamente
--   2. metricas_cliente: agrega R, F, M por customer_unique_id
--   3. scores: aplica NTILE(5) para quintis de cada dimensão
--   4. SELECT final: nomeia segmentos via CASE WHEN
--
-- Sobre o NTILE e Recency:
--   NTILE(5) OVER (ORDER BY recency DESC) garante que
--   clientes mais recentes (menor recency) recebem score 5.
--   O ORDER BY DESC inverte a lógica porque NTILE atribui
--   partição 1 aos primeiros valores.

WITH data_referencia AS (
  SELECT (MAX(order_purchase_timestamp)::DATE + INTERVAL '1 day')::DATE AS ref_date
  FROM orders
),

-- Calcula as 3 métricas RFM por cliente
-- JOIN com order_items para obter o valor monetário (price + freight)
metricas_cliente AS (
  SELECT
    c.customer_unique_id,
    DATE_DIFF(
      'day',
      MAX(o.order_purchase_timestamp)::DATE,
      (SELECT ref_date FROM data_referencia)
    ) AS recency,
    COUNT(DISTINCT o.order_id) AS frequency,
    ROUND(CAST(SUM(oi.price + oi.freight_value) AS NUMERIC), 2) AS monetary
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),

-- Aplica NTILE(5) para cada dimensão
-- NTILE divide os clientes em 5 grupos de tamanho ~igual
-- Score 5 = melhor quintil, Score 1 = pior quintil
scores AS (
  SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    -- Recency: ORDER BY DESC porque menor recency = melhor
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
    -- Frequency: ORDER BY ASC porque maior frequency = melhor
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    -- Monetary: ORDER BY ASC porque maior monetary = melhor
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
  FROM metricas_cliente
)

-- Nomeia segmentos baseado na combinação de scores
-- A ordem do CASE WHEN importa: a primeira condição verdadeira vence.
-- Isso cria uma hierarquia: Champions > Loyal > At Risk > ...
SELECT
  customer_unique_id,
  recency,
  frequency,
  monetary,
  r_score,
  f_score,
  m_score,
  CASE
    -- Champions: recentes, frequentes, alto valor
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
    -- Loyal: frequentes (independente de recência)
    WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
    -- New Customers: compraram recentemente, poucos pedidos
    WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
    -- Promising: recentes-ish, poucos pedidos, bom valor
    WHEN r_score >= 3 AND f_score <= 2 AND m_score >= 3 THEN 'Promising'
    -- At Risk: sumiram, mas eram frequentes
    WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
    -- Need Attention: sumiram, mas gastavam bem
    WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Need Attention'
    -- Lost: sumiram, pouca frequência, baixo valor
    WHEN r_score = 1 AND f_score = 1 AND m_score = 1 THEN 'Lost'
    -- Hibernating: todos os demais
    ELSE 'Hibernating'
  END AS segmento
FROM scores
ORDER BY r_score DESC, f_score DESC, m_score DESC;


-- -------------------------------------------------
-- 2. Perfil agregado por segmento
-- -------------------------------------------------
-- Resume as métricas médias de cada segmento para
-- facilitar a comparação no dashboard (barras, treemap).

WITH data_referencia AS (
  SELECT (MAX(order_purchase_timestamp)::DATE + INTERVAL '1 day')::DATE AS ref_date
  FROM orders
),
metricas_cliente AS (
  SELECT
    c.customer_unique_id,
    DATE_DIFF(
      'day',
      MAX(o.order_purchase_timestamp)::DATE,
      (SELECT ref_date FROM data_referencia)
    ) AS recency,
    COUNT(DISTINCT o.order_id) AS frequency,
    ROUND(CAST(SUM(oi.price + oi.freight_value) AS NUMERIC), 2) AS monetary
  FROM orders o
  JOIN customers c ON o.customer_id = c.customer_id
  JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
),
scores AS (
  SELECT
    customer_unique_id,
    recency,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
  FROM metricas_cliente
),
segmentado AS (
  SELECT
    *,
    CASE
      WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
      WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
      WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
      WHEN r_score >= 3 AND f_score <= 2 AND m_score >= 3 THEN 'Promising'
      WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
      WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Need Attention'
      WHEN r_score = 1 AND f_score = 1 AND m_score = 1 THEN 'Lost'
      ELSE 'Hibernating'
    END AS segmento
  FROM scores
)
SELECT
  segmento,
  COUNT(*) AS contagem,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM segmentado), 2) AS percentual,
  ROUND(AVG(recency), 1) AS recencia_media,
  ROUND(AVG(frequency), 2) AS frequencia_media,
  ROUND(CAST(AVG(monetary) AS NUMERIC), 2) AS monetario_medio,
  ROUND(AVG(r_score), 2) AS r_score_medio,
  ROUND(AVG(f_score), 2) AS f_score_medio,
  ROUND(AVG(m_score), 2) AS m_score_medio
FROM segmentado
GROUP BY segmento
ORDER BY contagem DESC;
