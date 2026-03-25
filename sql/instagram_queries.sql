-- ============================================================
-- Instagram Analytics — Queries SQL
-- Base de datos: social_media.db / tablas: instagram_reels, instagram_daily
-- Periodo: 24 Feb - 24 Mar 2026
-- ============================================================


-- 1. Resumen global del periodo
SELECT
    COUNT(*)                            AS total_reels,
    SUM(visualizaciones)                AS total_vistas,
    ROUND(AVG(visualizaciones), 0)      AS vistas_medias,
    ROUND(AVG(engagement_rate), 2)      AS er_medio,
    ROUND(AVG(save_rate), 2)            AS save_rate_medio,
    ROUND(AVG(share_rate), 2)           AS share_rate_medio,
    SUM(seguidores_ganados)             AS seguidores_ganados
FROM instagram_reels;


-- 2. Rendimiento por tematica (solo temas con mas de 1 reel)
SELECT
    tema,
    COUNT(*)                            AS reels,
    ROUND(AVG(engagement_rate), 2)      AS er_medio,
    ROUND(AVG(save_rate), 2)            AS save_rate_medio,
    ROUND(AVG(share_rate), 2)           AS share_rate_medio,
    SUM(seguidores_ganados)             AS seguidores_totales,
    MAX(engagement_rate)                AS er_maximo
FROM instagram_reels
GROUP BY tema
HAVING COUNT(*) > 1
ORDER BY er_medio DESC;


-- 3. Rendimiento por franja horaria
SELECT
    franja,
    COUNT(*)                            AS reels,
    ROUND(AVG(engagement_rate), 2)      AS er_medio,
    ROUND(AVG(save_rate), 2)            AS save_rate_medio,
    ROUND(AVG(guardados), 1)            AS guardados_medios,
    SUM(seguidores_ganados)             AS seguidores
FROM instagram_reels
GROUP BY franja
ORDER BY er_medio DESC;


-- 4. Rendimiento por dia de la semana
SELECT
    dia_semana,
    COUNT(*)                            AS reels,
    ROUND(AVG(engagement_rate), 2)      AS er_medio,
    ROUND(AVG(save_rate), 2)            AS save_rate_medio,
    ROUND(AVG(visualizaciones), 0)      AS vistas_medias
FROM instagram_reels
GROUP BY dia_semana
ORDER BY er_medio DESC;


-- 5. Ranking de reels con percentil de engagement
SELECT
    descripcion_corta,
    fecha,
    tema,
    engagement_rate,
    save_rate,
    RANK() OVER (ORDER BY engagement_rate DESC) AS rank_er,
    ROUND(
        100.0 * RANK() OVER (ORDER BY engagement_rate DESC) / COUNT(*) OVER (),
        1
    ) AS percentil
FROM instagram_reels
ORDER BY rank_er;


-- 6. Top 3 reels por tematica (PARTITION BY)
SELECT *
FROM (
    SELECT
        tema,
        descripcion_corta,
        fecha,
        engagement_rate,
        save_rate,
        ROW_NUMBER() OVER (PARTITION BY tema ORDER BY engagement_rate DESC) AS rank_en_tema
    FROM instagram_reels
)
WHERE rank_en_tema <= 3
ORDER BY tema, rank_en_tema;


-- 7. Reels que superan la media de su propia tematica (subquery correlacionada)
SELECT
    r.fecha,
    r.tema,
    r.descripcion_corta,
    r.engagement_rate,
    ROUND((
        SELECT AVG(r2.engagement_rate)
        FROM instagram_reels r2
        WHERE r2.tema = r.tema
    ), 2) AS media_er_tema,
    ROUND(r.engagement_rate - (
        SELECT AVG(r2.engagement_rate)
        FROM instagram_reels r2
        WHERE r2.tema = r.tema
    ), 2) AS diferencia_vs_tema
FROM instagram_reels r
WHERE r.engagement_rate > (
    SELECT AVG(r2.engagement_rate)
    FROM instagram_reels r2
    WHERE r2.tema = r.tema
)
ORDER BY diferencia_vs_tema DESC;


-- 8. Evolucion acumulada de seguidores con media movil 7 dias (metricas diarias)
SELECT
    fecha,
    seguidores_ganados,
    SUM(seguidores_ganados) OVER (ORDER BY fecha)  AS seguidores_acumulados,
    ROUND(AVG(seguidores_ganados) OVER (
        ORDER BY fecha ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 1)                                           AS media_movil_7d,
    SUM(visualizaciones) OVER (ORDER BY fecha)     AS vistas_acumuladas
FROM instagram_daily
ORDER BY fecha;


-- 9. CTE: reels que superan la media simultaneamente en ER, save rate y share rate
WITH medias AS (
    SELECT
        AVG(engagement_rate) AS avg_er,
        AVG(save_rate)       AS avg_save,
        AVG(share_rate)      AS avg_share
    FROM instagram_reels
)
SELECT
    r.fecha,
    r.descripcion_corta,
    r.tema,
    r.engagement_rate,
    r.save_rate,
    r.share_rate
FROM instagram_reels r
CROSS JOIN medias m
WHERE r.engagement_rate > m.avg_er
  AND r.save_rate       > m.avg_save
  AND r.share_rate      > m.avg_share
ORDER BY r.engagement_rate DESC;


-- 10. Comparacion reel vs reel anterior (LAG) y siguiente (LEAD)
SELECT
    fecha,
    descripcion_corta,
    engagement_rate,
    LAG(engagement_rate)  OVER (ORDER BY fecha)  AS er_reel_anterior,
    LEAD(engagement_rate) OVER (ORDER BY fecha)  AS er_reel_siguiente,
    ROUND(engagement_rate - LAG(engagement_rate) OVER (ORDER BY fecha), 2) AS variacion
FROM instagram_reels
ORDER BY fecha;
