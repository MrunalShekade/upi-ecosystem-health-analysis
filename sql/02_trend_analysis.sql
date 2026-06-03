-- Query 2: Monthly trend analysis for worst performing banks
-- Shows TD% trajectory over time to identify improving vs deteriorating banks

SELECT 
    bank_name,
    file_type,
    year,
    month,
    td_pct,
    approved_pct,
    total_volume_mn,
    ROUND(AVG(td_pct) OVER (
        PARTITION BY bank_name, file_type 
        ORDER BY year, month 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )::numeric, 2) AS rolling_3m_td_pct
FROM upi_data
WHERE bank_name IN (
    'Uttar Pradesh Gramin Bank',
    'Andhra Pradesh Grameena Bank',
    'Karnataka Grameena Bank',
    'India Post Payments Bank Ltd'
)
AND file_type = 'remitter'
ORDER BY bank_name, year, month;