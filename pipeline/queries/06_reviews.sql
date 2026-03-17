-- Reviews e Satisfacao: distribuicao, NPS, categorias, atraso, comentarios

-- Resultado 1: distribuicao de scores
-- nome: reviews_distribuicao
SELECT
  review_score AS score,
  COUNT(*) AS contagem,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM order_reviews), 2) AS percentual
FROM order_reviews
GROUP BY review_score
ORDER BY review_score;

-- Resultado 2: NPS (Net Promoter Score)
-- nome: reviews_nps
WITH classificacao AS (
  SELECT
    CASE
      WHEN review_score = 5 THEN 'promotor'
      WHEN review_score >= 3 THEN 'neutro'
      ELSE 'detrator'
    END AS tipo
  FROM order_reviews
)
SELECT
  COUNT(CASE WHEN tipo = 'promotor' THEN 1 END) AS promotores,
  COUNT(CASE WHEN tipo = 'neutro' THEN 1 END) AS neutros,
  COUNT(CASE WHEN tipo = 'detrator' THEN 1 END) AS detratores,
  COUNT(*) AS total,
  ROUND(
    COUNT(CASE WHEN tipo = 'promotor' THEN 1 END) * 100.0 / COUNT(*), 2
  ) AS pct_promotores,
  ROUND(
    COUNT(CASE WHEN tipo = 'detrator' THEN 1 END) * 100.0 / COUNT(*), 2
  ) AS pct_detratores,
  ROUND(
    COUNT(CASE WHEN tipo = 'promotor' THEN 1 END) * 100.0 / COUNT(*)
    - COUNT(CASE WHEN tipo = 'detrator' THEN 1 END) * 100.0 / COUNT(*),
    2
  ) AS nps
FROM classificacao;

-- Resultado 3: score medio por categoria de produto
-- nome: reviews_categorias
SELECT
  COALESCE(ct.product_category_name_english, p.product_category_name, 'sem_categoria') AS categoria,
  COUNT(*) AS total_reviews,
  ROUND(AVG(r.review_score), 2) AS score_medio,
  COUNT(CASE WHEN r.review_score >= 4 THEN 1 END) AS reviews_positivas,
  COUNT(CASE WHEN r.review_score <= 2 THEN 1 END) AS reviews_negativas
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY COALESCE(ct.product_category_name_english, p.product_category_name, 'sem_categoria')
HAVING COUNT(*) >= 2
ORDER BY score_medio DESC;

-- Resultado 4: relacao atraso x review score
-- nome: reviews_atraso
WITH entregas AS (
  SELECT
    r.review_score,
    DATE_DIFF('day', o.order_estimated_delivery_date, o.order_delivered_customer_date) AS dias_atraso
  FROM orders o
  JOIN order_reviews r ON o.order_id = r.order_id
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT
  CASE
    WHEN dias_atraso <= 0 THEN 'No prazo ou antes'
    WHEN dias_atraso BETWEEN 1 AND 3 THEN '1-3 dias'
    WHEN dias_atraso BETWEEN 4 AND 7 THEN '4-7 dias'
    WHEN dias_atraso BETWEEN 8 AND 14 THEN '8-14 dias'
    WHEN dias_atraso BETWEEN 15 AND 30 THEN '15-30 dias'
    ELSE 'Mais de 30 dias'
  END AS faixa_atraso,
  COUNT(*) AS contagem,
  ROUND(AVG(review_score), 2) AS score_medio,
  MIN(dias_atraso) AS min_dias,
  MAX(dias_atraso) AS max_dias
FROM entregas
GROUP BY
  CASE
    WHEN dias_atraso <= 0 THEN 'No prazo ou antes'
    WHEN dias_atraso BETWEEN 1 AND 3 THEN '1-3 dias'
    WHEN dias_atraso BETWEEN 4 AND 7 THEN '4-7 dias'
    WHEN dias_atraso BETWEEN 8 AND 14 THEN '8-14 dias'
    WHEN dias_atraso BETWEEN 15 AND 30 THEN '15-30 dias'
    ELSE 'Mais de 30 dias'
  END
ORDER BY min_dias;

-- Resultado 5: contagem de reviews com e sem comentario
-- nome: reviews_comentarios
SELECT
  COUNT(CASE WHEN review_comment_message IS NOT NULL AND review_comment_message != '' THEN 1 END) AS com_comentario,
  COUNT(CASE WHEN review_comment_message IS NULL OR review_comment_message = '' THEN 1 END) AS sem_comentario,
  COUNT(*) AS total,
  ROUND(
    COUNT(CASE WHEN review_comment_message IS NOT NULL AND review_comment_message != '' THEN 1 END) * 100.0 / COUNT(*), 2
  ) AS pct_com_comentario
FROM order_reviews;
