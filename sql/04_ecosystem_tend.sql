-- QUERY 4: ECOSYSTEM HEALTH TREND ANALYSIS
-- Purpose:
-- Track monthly UPI ecosystem performance over time using
-- volume-weighted success and failure rates.
--
-- Key Metrics:
-- - Ecosystem Approved %
-- - Ecosystem Technical Decline %
-- - Ecosystem Business Decline %
-- - Total Transaction Volume
-- - Number of Banks Reporting
--
-- Data Scope:
-- Remitter transactions only
-- Period: Jan 2024 - Feb 2026
-- ============================================================

SELECT 
    year,
    month,
    ROUND(
        (SUM(approved_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0))::numeric
    , 2) AS ecosystem_approved_pct,
    ROUND(
        (SUM(td_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0))::numeric
    , 2) AS ecosystem_td_pct,
    ROUND(
        (SUM(bd_pct * total_volume_mn) / NULLIF(SUM(total_volume_mn), 0))::numeric
    , 2) AS ecosystem_bd_pct,
    ROUND(SUM(total_volume_mn)::numeric, 2) AS total_volume_mn,
    COUNT(DISTINCT bank_name) AS banks_reporting
FROM upi_data
WHERE file_type = 'remitter'
GROUP BY year, month
ORDER BY year, month;