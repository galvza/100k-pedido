-- Sazonalidade: serie temporal mensal, padrao semanal, padrao horario

-- Resultado 1: serie temporal mensal com media movel e MoM growth
-- nome: sazonalidade_mensal
WITH mensal AS (
  SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp)::DATE AS mes,
    COUNT(DISTINCT o.order_id) AS pedidos,
    ROUND(CAST(SUM(oi.price + oi.freight_value) AS NUMERIC), 2) AS receita
  FROM orders o
  JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)::DATE
)
SELECT
  mes,
  pedidos,
  receita,
  CASE
    WHEN ROW_NUMBER() OVER (ORDER BY mes) >= 3
    THEN ROUND(CAST(AVG(receita) OVER (
      ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS NUMERIC), 2)
    ELSE NULL
  END AS media_movel_3m,
  CASE
    WHEN LAG(receita) OVER (ORDER BY mes) IS NOT NULL
      AND LAG(receita) OVER (ORDER BY mes) > 0
    THEN ROUND(CAST(
      (receita - LAG(receita) OVER (ORDER BY mes))
      / LAG(receita) OVER (ORDER BY mes)
    AS NUMERIC), 4)
    ELSE NULL
  END AS mom_growth
FROM mensal
ORDER BY mes;

-- Resultado 2: padrao por dia da semana
-- nome: sazonalidade_semanal
WITH semanal_por_semana AS (
  SELECT
    EXTRACT(DOW FROM o.order_purchase_timestamp)::INTEGER AS dia_semana,
    DATE_TRUNC('week', o.order_purchase_timestamp)::DATE AS semana,
    COUNT(DISTINCT o.order_id) AS pedidos,
    ROUND(CAST(SUM(oi.price + oi.freight_value) AS NUMERIC), 2) AS receita
  FROM orders o
  JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY
    EXTRACT(DOW FROM o.order_purchase_timestamp)::INTEGER,
    DATE_TRUNC('week', o.order_purchase_timestamp)::DATE
)
SELECT
  dia_semana,
  ROUND(AVG(pedidos), 2) AS pedidos_medio,
  ROUND(CAST(AVG(receita) AS NUMERIC), 2) AS receita_media,
  ROUND(CAST(AVG(receita / NULLIF(pedidos, 0)) AS NUMERIC), 2) AS ticket_medio
FROM semanal_por_semana
GROUP BY dia_semana
ORDER BY dia_semana;

-- Resultado 3: padrao por hora do dia
-- nome: sazonalidade_horaria
SELECT
  EXTRACT(HOUR FROM o.order_purchase_timestamp)::INTEGER AS hora,
  COUNT(DISTINCT o.order_id) AS pedidos,
  ROUND(CAST(SUM(oi.price + oi.freight_value) AS NUMERIC), 2) AS receita
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY EXTRACT(HOUR FROM o.order_purchase_timestamp)::INTEGER
ORDER BY hora;
