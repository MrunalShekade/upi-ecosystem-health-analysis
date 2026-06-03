
-- Query 1: Bank failure rate rankings using volume-weighted TD%
-- Volume-weighted average gives more weight to high-traffic months
-- HAVING COUNT(*) >= 12 ensures rankings are based on sufficient data

SELECT 
    bank_name,
    file_type,
    ROUND(
        (SUM(td_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0))::numeric
    , 2) AS weighted_td_pct,
    ROUND(
        (SUM(bd_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0))::numeric
    , 2) AS weighted_bd_pct,
    ROUND(
        (SUM(approved_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0))::numeric
    , 2) AS weighted_approved_pct,
    ROUND(SUM(total_volume_mn)::numeric, 2) AS total_volume_mn,
    COUNT(*) AS months_present
FROM upi_data
GROUP BY bank_name, file_type
HAVING COUNT(*) >= 12
ORDER BY weighted_td_pct DESC
LIMIT 20;