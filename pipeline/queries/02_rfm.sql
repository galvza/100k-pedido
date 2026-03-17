-- RFM Segmentation: scores por cliente e agregacao por segmento

-- Resultado 1: scores RFM por cliente
-- nome: rfm_scores
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
)
SELECT
  customer_unique_id,
  recency,
  frequency,
  monetary,
  r_score,
  f_score,
  m_score,
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
ORDER BY r_score DESC, f_score DESC, m_score DESC;

-- Resultado 2: perfil agregado por segmento
-- nome: rfm_segmentos
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
