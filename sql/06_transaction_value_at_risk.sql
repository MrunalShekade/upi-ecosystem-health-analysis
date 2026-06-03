-- Query 6: Revenue impact of technical failures
-- Calculates failed transaction volume and transaction value at risk per bank
-- Assumption: avg ticket size Rs 1576 (RBI FY2024-25 published figure)
-- Focus on TD% only — bank controllable failures

WITH bank_monthly AS (
    SELECT
        bank_name,
        file_type,
        year,
        month,
        total_volume_mn,
        td_pct,

        -- Failed transactions in millions
        ROUND((total_volume_mn * td_pct / 100)::numeric, 4) AS failed_volume_mn,

        -- Transaction Value at Risk in crores
        ROUND(
            (total_volume_mn * td_pct / 100 * 1576 / 10)::numeric,
            2
        ) AS transaction_value_at_risk_crores

    FROM upi_data
    WHERE file_type = 'remitter'
),

bank_totals AS (
    SELECT
        bank_name,
        ROUND(SUM(total_volume_mn)::numeric, 2) AS total_volume_mn,
        ROUND(SUM(failed_volume_mn)::numeric, 4) AS total_failed_mn,
        ROUND(SUM(transaction_value_at_risk_crores)::numeric, 2) AS total_transaction_value_at_risk_crores,
        COUNT(*) AS months_present
    FROM bank_monthly
    GROUP BY bank_name
    HAVING COUNT(*) >= 12
)

SELECT
    bank_name,
    total_volume_mn,
    total_failed_mn,
    total_transaction_value_at_risk_crores,
    ROUND(
        (total_failed_mn / NULLIF(total_volume_mn, 0) * 100)::numeric,
        2
    ) AS overall_td_pct,
    months_present
FROM bank_totals
ORDER BY total_transaction_value_at_risk_crores DESC
LIMIT 20;