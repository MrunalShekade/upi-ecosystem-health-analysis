-- Query 3: Remitter vs Beneficiary comparison
-- Finds banks that are bad at both roles — most damaging to ecosystem
-- A bank bad at both touches every transaction it's involved in

SELECT 
    r.bank_name,
    ROUND(r.weighted_td_pct::numeric, 2) AS remitter_td_pct,
    ROUND(b.weighted_td_pct::numeric, 2) AS beneficiary_td_pct,
    ROUND(((r.weighted_td_pct + b.weighted_td_pct) / 2)::numeric, 2) AS combined_td_pct,
    ROUND(r.total_volume_mn::numeric, 2) AS remitter_volume,
    ROUND(b.total_volume_mn::numeric, 2) AS beneficiary_volume
FROM (
    SELECT 
        bank_name,
        SUM(td_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0) AS weighted_td_pct,
        SUM(total_volume_mn) AS total_volume_mn
    FROM upi_data
    WHERE file_type = 'remitter'
    GROUP BY bank_name
    HAVING COUNT(*) >= 12
) r
JOIN (
    SELECT 
        bank_name,
        SUM(td_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0) AS weighted_td_pct,
        SUM(total_volume_mn) AS total_volume_mn
    FROM upi_data
    WHERE file_type = 'beneficiary'
    GROUP BY bank_name
    HAVING COUNT(*) >= 12
) b ON r.bank_name = b.bank_name
ORDER BY combined_td_pct DESC
LIMIT 20;