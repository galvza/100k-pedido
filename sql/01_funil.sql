-- ===========================================
-- Cap. 1: Funil de Vendas
-- Técnicas: CTE, CASE WHEN, agregações condicionais, DATE_DIFF
-- Dataset: Olist Brazilian E-Commerce (100k pedidos)
-- ===========================================
--
-- Este capítulo mapeia as etapas do pedido no marketplace:
-- Compra → Aprovação do pagamento → Envio → Entrega
--
-- O funil é construído a partir dos timestamps da tabela orders.
-- "Funil" aqui se refere ao pipeline de fulfillment, não ao funil
-- de navegação (o dataset não tem dados de abandono de carrinho).
--
-- Três resultados são gerados:
--   1. Contagem de pedidos por status final
--   2. Conversão entre etapas com tempo médio
--   3. Distribuição do tempo total de entrega em faixas
-- ===========================================


-- -------------------------------------------------
-- 1. Contagem de pedidos por status
-- -------------------------------------------------
-- Mostra a distribuição dos status finais dos pedidos.
-- O status 'delivered' é o mais comum (~97% no dataset real).
-- Cancelamentos e outros status representam perdas no funil.

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


-- -------------------------------------------------
-- 2. Conversão entre etapas do funil
-- -------------------------------------------------
-- Cada etapa é definida pela existência do timestamp correspondente:
--   - Compra: order_purchase_timestamp (sempre preenchido)
--   - Aprovação: order_approved_at (NULL se pagamento não aprovado)
--   - Envio: order_delivered_carrier_date (NULL se não enviado)
--   - Entrega: order_status = 'delivered'
--
-- A taxa_conversao é calculada em relação à etapa anterior.
-- O tempo_medio_dias é o intervalo médio entre a etapa anterior e a atual.
--
-- Técnicas: CTE com agregações condicionais (COUNT + CASE WHEN),
-- subqueries correlacionadas para cálculo de tempo, UNION ALL
-- para montar o resultado em formato de funil.

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


-- -------------------------------------------------
-- 3. Distribuição do tempo de entrega
-- -------------------------------------------------
-- Tempo total = purchase → delivered_customer_date
-- Agrupado em faixas pra visualização como histograma.
--
-- Faixas escolhidas:
--   0-7 dias: entrega rápida
--   8-14 dias: dentro do prazo típico
--   15-30 dias: entrega lenta
--   30+ dias: outliers / atrasos graves
--
-- Técnica: CTE com DATE_DIFF + CASE WHEN pra criar faixas.

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
