-- ===========================================
-- Cap. 5: Sazonalidade
-- Técnicas: DATE_TRUNC, EXTRACT, Window Functions (AVG OVER ROWS,
--           LAG, ROW_NUMBER), NULLIF, média móvel
-- Dataset: Olist Brazilian E-Commerce (100k pedidos)
-- ===========================================
--
-- Identifica padrões temporais de vendas em 3 granularidades:
--   1. Mensal — série temporal com média móvel e crescimento MoM
--   2. Dia da semana — padrão semanal (domingo=0 a sábado=6)
--   3. Hora do dia — distribuição horária de pedidos
--
-- Apenas pedidos 'delivered' são considerados para métricas
-- confiáveis de receita (pedidos cancelados distorceriam).
--
-- O dataset cobre jan/2017 a ago/2018 (~20 meses).
-- Picos esperados: Black Friday (nov), Natal (dez).
-- ===========================================


-- -------------------------------------------------
-- 1. Série temporal mensal
-- -------------------------------------------------
-- Cada linha = 1 mês com:
--   - pedidos e receita bruta
--   - média móvel de 3 meses (suaviza ruído)
--   - MoM growth (variação percentual mês a mês)
--
-- A média móvel usa AVG() OVER (ROWS BETWEEN 2 PRECEDING AND
-- CURRENT ROW), que considera o mês atual + 2 anteriores.
-- Os 2 primeiros meses retornam NULL (não há janela completa).
--
-- O MoM growth usa LAG() para comparar com o mês anterior.
-- Primeiro mês retorna NULL (não há mês anterior).

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
  -- Média móvel: NULL nos 2 primeiros meses (janela incompleta)
  CASE
    WHEN ROW_NUMBER() OVER (ORDER BY mes) >= 3
    THEN ROUND(CAST(AVG(receita) OVER (
      ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS NUMERIC), 2)
    ELSE NULL
  END AS media_movel_3m,
  -- MoM growth: (receita_atual - receita_anterior) / receita_anterior
  -- NULL no primeiro mês (sem mês anterior para comparar)
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


-- -------------------------------------------------
-- 2. Padrão por dia da semana
-- -------------------------------------------------
-- Calcula a média de pedidos e receita por dia da semana,
-- agrupando primeiro por (dia_semana, semana) e depois
-- tirando a média entre semanas.
--
-- Isso evita que semanas com mais dias úteis (feriados)
-- distorçam a comparação entre dias.
--
-- EXTRACT(DOW): 0=domingo, 1=segunda, ..., 6=sábado (padrão ISO)

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
  -- Ticket médio = receita / pedidos por semana, depois média
  ROUND(CAST(AVG(receita / NULLIF(pedidos, 0)) AS NUMERIC), 2) AS ticket_medio
FROM semanal_por_semana
GROUP BY dia_semana
ORDER BY dia_semana;


-- -------------------------------------------------
-- 3. Padrão por hora do dia
-- -------------------------------------------------
-- Distribuição absoluta de pedidos e receita por hora.
-- Espera-se pico entre 10h-14h e 19h-22h (horário comercial
-- e noite), com vale na madrugada (2h-6h).

SELECT
  EXTRACT(HOUR FROM o.order_purchase_timestamp)::INTEGER AS hora,
  COUNT(DISTINCT o.order_id) AS pedidos,
  ROUND(CAST(SUM(oi.price + oi.freight_value) AS NUMERIC), 2) AS receita
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY EXTRACT(HOUR FROM o.order_purchase_timestamp)::INTEGER
ORDER BY hora;
