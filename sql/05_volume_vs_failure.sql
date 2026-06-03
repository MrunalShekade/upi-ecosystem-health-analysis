-- Query 5: Volume vs failure rate correlation
-- Tests whether high volume banks have better or worse TD%
-- Buckets banks by volume tier and compares average TD%

WITH bank_summary AS (
    SELECT 
        bank_name,
        SUM(td_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0) AS weighted_td_pct,
        SUM(total_volume_mn) AS total_volume_mn,
        COUNT(*) AS months_present
    FROM upi_data
    WHERE file_type = 'remitter'
    GROUP BY bank_name
    HAVING COUNT(*) >= 12
),
volume_tiers AS (
    SELECT 
        bank_name,
        weighted_td_pct,
        total_volume_mn,
        CASE 
            WHEN total_volume_mn >= 10000 THEN '1. Very High (10000+ Mn)'
            WHEN total_volume_mn >= 3000  THEN '2. High (3000-10000 Mn)'
            WHEN total_volume_mn >= 1000  THEN '3. Medium (1000-3000 Mn)'
            WHEN total_volume_mn >= 300   THEN '4. Low (300-1000 Mn)'
            ELSE '5. Very Low (<300 Mn)'
        END AS volume_tier
    FROM bank_summary
)
SELECT 
    volume_tier,
    COUNT(*) AS bank_count,
    ROUND(AVG(weighted_td_pct)::numeric, 2) AS avg_td_pct,
    ROUND(MIN(weighted_td_pct)::numeric, 2) AS min_td_pct,
    ROUND(MAX(weighted_td_pct)::numeric, 2) AS max_td_pct,
    ROUND(SUM(total_volume_mn)::numeric, 2) AS total_volume_mn
FROM volume_tiers
GROUP BY volume_tier
ORDER BY volume_tier;