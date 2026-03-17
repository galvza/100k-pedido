-- Funil de Vendas: status, conversao entre etapas, tempos medios, distribuicao de entrega

-- Resultado 1: contagem por status
-- nome: funil_status
WITH total AS (
  SELECT COUNT(*) AS total_pedidos FROM orders
)
SELECT
  o.order_status AS status,
  COUNT(*) AS contagem,
  ROUND(COUNT(*) * 100.0 / t.total_pedidos, 2) AS percentual
FROM orders o, total t
GROUP BY o.order_status, t.total_pedidos
ORDER BY contagem DESC;

-- Resultado 2: conversao entre etapas
-- nome: funil_conversao
WITH etapas AS (
  SELECT
    COUNT(*) AS compra,
    COUNT(CASE WHEN order_approved_at IS NOT NULL THEN 1 END) AS aprovacao,
    COUNT(CASE WHEN order_delivered_carrier_date IS NOT NULL THEN 1 END) AS envio,
    COUNT(CASE WHEN order_status = 'delivered' THEN 1 END) AS entrega,
    COUNT(CASE WHEN order_status = 'canceled' THEN 1 END) AS cancelado
  FROM orders
)
SELECT
  'Compra' AS etapa,
  compra AS pedidos,
  1.0 AS taxa_conversao,
  0.0 AS tempo_medio_dias
FROM etapas

UNION ALL

SELECT
  'Aprovacao' AS etapa,
  aprovacao AS pedidos,
  ROUND(aprovacao * 1.0 / compra, 4) AS taxa_conversao,
  (
    SELECT ROUND(AVG(
      DATE_DIFF('hour', order_purchase_timestamp, order_approved_at) / 24.0
    ), 2)
    FROM orders
    WHERE order_approved_at IS NOT NULL
  ) AS tempo_medio_dias
FROM etapas

UNION ALL

SELECT
  'Envio' AS etapa,
  envio AS pedidos,
  ROUND(envio * 1.0 / aprovacao, 4) AS taxa_conversao,
  (
    SELECT ROUND(AVG(
      DATE_DIFF('hour', order_approved_at, order_delivered_carrier_date) / 24.0
    ), 2)
    FROM orders
    WHERE order_approved_at IS NOT NULL
      AND order_delivered_carrier_date IS NOT NULL
  ) AS tempo_medio_dias
FROM etapas

UNION ALL

SELECT
  'Entrega' AS etapa,
  entrega AS pedidos,
  ROUND(entrega * 1.0 / envio, 4) AS taxa_conversao,
  (
    SELECT ROUND(AVG(
      DATE_DIFF('hour', order_delivered_carrier_date, order_delivered_customer_date) / 24.0
    ), 2)
    FROM orders
    WHERE order_delivered_carrier_date IS NOT NULL
      AND order_delivered_customer_date IS NOT NULL
  ) AS tempo_medio_dias
FROM etapas;

-- Resultado 3: distribuicao do tempo de entrega (compra ate entrega ao cliente)
-- nome: funil_tempos
WITH entregas AS (
  SELECT
    DATE_DIFF('day', order_purchase_timestamp, order_delivered_customer_date) AS dias_entrega
  FROM orders
  WHERE order_status = 'delivered'
    AND order_delivered_customer_date IS NOT NULL
)
SELECT
  CASE
    WHEN dias_entrega BETWEEN 0 AND 7 THEN '0-7 dias'
    WHEN dias_entrega BETWEEN 8 AND 14 THEN '8-14 dias'
    WHEN dias_entrega BETWEEN 15 AND 30 THEN '15-30 dias'
    ELSE '30+ dias'
  END AS faixa,
  COUNT(*) AS contagem,
  ROUND(AVG(dias_entrega), 1) AS media_dias_na_faixa,
  MIN(dias_entrega) AS min_dias,
  MAX(dias_entrega) AS max_dias
FROM entregas
GROUP BY
  CASE
    WHEN dias_entrega BETWEEN 0 AND 7 THEN '0-7 dias'
    WHEN dias_entrega BETWEEN 8 AND 14 THEN '8-14 dias'
    WHEN dias_entrega BETWEEN 15 AND 30 THEN '15-30 dias'
    ELSE '30+ dias'
  END
ORDER BY min_dias;
