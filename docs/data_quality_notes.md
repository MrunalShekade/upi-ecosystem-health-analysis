# Data Quality Notes
# issues:

1. Column Name Inconsistencies Across NPCI Files

NPCI uses different column names across months for the same data.
Issue                        Example 
Bank name column     "UPI Beneficiary Banks" vs "UPI Beneficiary  banks"
                      vs "upi_remitter_banks"
Sr. No. column        "Sr.No." vs "Sr No." vs "Sr. No.
"BD% column           "BD%" vs "BD %"

Fix: All files read by column position (index 1) instead of column name. Column names standardised after reading.
Script: scripts/03_clean_and_load.py
---

2. Bank Name Inconsistencies

165 unique bank name strings found across 52 files, mapping to approximately 82 actual banks. Variations include capitalisation differences, legal suffix variations (Ltd/Limited/Ltd.), and abbreviated names.

Fix: bank_master.csv created mapping every raw name to one standard name. Applied during cleaning before database load.

Standardisation rule: Banks appearing with "Ltd" at least once use "Ltd" in standard name. Applied consistently across all banks.

Script: scripts/02_extract_banks.py extracts unique names, 
        scripts/03_clean_and_load.py applies mappings.
---

3. Excluded Entities

The following appeared in NPCI data but were excluded as they are not UPI banking participants:

Entity                                       Reason
------------------------------------------------------------------------------
Axis Bank Credit Card            Credit card division, duplicate of Axis Bank
------------------------------------------------------------------------------
HDFC Bank Credit Card HCB        Credit card division, duplicate of HDFC Bank
------------------------------------------------------------------------------
ICICI Bank Credit Card           Credit card division, duplicate of ICICI Bank
------------------------------------------------------------------------------
SBI Cards and Payment            Credit card division, duplicate of SBI
Servies Limited
------------------------------------------------------------------------------
ONE MOBIKWIK SYSTEMS LIMITED      Payments wallet, not a licensed bank
------------------------------------------------------------------------------
One Mobikwik Systems Limited      Payments wallet, not a licensed bank
------------------------------------------------------------------------------
One Mobikwik Systems Pvt - Ltd    Payments wallet, not a licensed bank
------------------------------------------------------------------------------
Tri O Tech Solutions Private      Fintech company, not a bank
Limited
------------------------------------------------------------------------------
Tri O Tech Solutions Private      Fintech company, not a bank
Ltd.
------------------------------------------------------------------------------
Fino Payments Bank Limited FIP    FIP transaction type, not a separate bank
------------------------------------------------------------------------------
Andhra Pradesh Grameena Vikas     IMPS transaction, not UPI
Bank - IMPS

Fix: All excluded entities marked as EXCLUDE in bank_master.csv and filtered out during cleaning.
---

4. RRB Mergers - One State One RRB Policy (May 2025)

The Government of India merged 26 Regional Rural Banks into 12 entities effective May 1, 2025. Pre-merger names appeared before May 2025, post-merger names after.

Pre-merger Banks                               Post-merger Entity

Andhra Pradesh Grameena Vikas Bank,        Andhra Pradesh Grameena Bank
Andhra Pragathi Grameena Bank,
Chaitanya Godavari Grameena Bank.

Baroda U.P. Bank,                           Uttar Pradesh Gramin Bank
Baroda UP Gramin Bank,
Sarva UP Gramin Bank.
  
Karnataka Gramin Bank,                       Karnataka Grameena Bank
Pragathi Krishna Gramin Bank.

Rajasthan Marudhara Gramin Bank.              Rajasthan Gramin Bank

Fix: All 26 pre-merger names mapped to post-merger entity name in 
bank_master.csv.

Limitation: Pre and post merger data treated as continuous for the same entity. Performance changes around May 2025 may reflect merger integration effects rather than actual performance changes.
---

5. Fincare Small Finance Bank Acquisition (2024)

Fincare Small Finance Bank was acquired by AU Small Finance Bank in 2024. Both names appeared in the dataset across different time periods.

Fix: All Fincare entries mapped to AU Small Finance Bank in bank_master.csv to maintain a continuous trend line.

Limitation: Pre-acquisition Fincare data and post-acquisition AU data may not be directly comparable due to operational integration.
---

6. Volume Number Format

All volume figures in raw data contain commas, e.g. "3,912.83",
which prevents direct numeric conversion and cannot be parsed as float directly.

Fix: Commas removed and values converted to float during cleaning.

Script: scripts/03_clean_and_load.py
---

7. Percentage Format

All percentage figures in raw data are strings e.g. "94.55%". Cannot be parsed as numeric values, float directly.

Fix: % sign removed and converted to float during cleaning.

Important- storage scale: Percentages are stored in the database on a 0-100 scale (e.g. 94.55, not 0.9455). All SQL queries, Python calculations, and Power BI DAX measures treat these values as percentages on a 0–100 scale. Never divide by 100 when querying, they are already in percentage form.

Script: scripts/03_clean_and_load.py
---

8. Percentage Scale Error (January–July 2025)

NPCI stored percentage values on a 0-1 scale instead of 0-100 scale for all banks for the 7 months January 2025 through July 2025. For example, 94.55% was stored as 0.9455 instead of 94.55. This affected all percentage columns (approved_pct, bd_pct, td_pct).

Affected period: year == 2025 AND month <= 7

Fix: Multiply all percentage columns by 100 when year == 2025 and month <= 7 in the clean_dataframe function.

Script: scripts/03_clean_and_load.py
---

9. Duplicate Rows from Bank Mergers

Pre-merger banks mapping to the same standard name created duplicate rows for the same bank, month, and file_type.

Example: Andhra Pradesh Grameena Vikas Bank and Andhra Pragathi Grameena Bank both appeared in the same months before May 2025 merger. Both mapped to Andhra Pradesh Grameena Bank, creating two rows per month.

Fix: Added volume-weighted aggregation using groupby() after bank name standardisation. Percentages recalculated as weighted averages, volumes summed.

Result: 34 duplicate rows merged into single rows. 
Detection method: GROUP BY bank_name, file_type, year, month HAVING COUNT(*) > 1 returns zero rows after fix.

Script: scripts/03_clean_and_load.py
---

10. Floating Point Precision

Some percentage values show floating point imprecision after volume-weighted aggregation. Example: 2.800000000003 instead of 2.8. This is a known Python float arithmetic limitation.

Fix: Does not affect analysis accuracy. Values are rounded to 2 decimal places in all SQL queries using ROUND().
---

11. Missing Months

Some banks are missing certain months entirely, they dropped out of the NPCI top 50 for that period. This is expected behaviour as the dataset only covers the top 50 banks by volume each month.

Example: Uttar Pradesh Gramin Bank has no entry for January 2026 in remitter data, likely dropped out of top 50 that month.

Impact: This is why all ranking SQL queries use HAVING COUNT(*) >= 12 to ensure only banks with sufficient data history are included in rankings.
---

12. Temporary Excel Lock Files

Excel creates temporary files starting with ~$ when a file is open. These appeared in data/raw/ during script runs and caused errors.

Fix: Added filter not f.startswith('~$') to file list in all three scripts to permanently exclude them.

Scripts: scripts/01_load_raw.py, 
         scripts/02_extract_banks.py, 
         scripts/03_clean_and_load.py
---

13. Source Data Error - Tamilnad Mercantile Bank Sep 2024

NPCI published an approved_pct of 124.22% for Tamilnad Mercantile Bank beneficiary in September 2024. This is mathematically impossible, percentages cannot exceed 100.

Fix: Set to NULL in database via np.nan in cleaning script. Excluded from percentage scale and sum tests in pytest. Affects 1 row out of 2,479.

Source: Verified in raw file data/raw/upi_beneficiary_2024_09.xlsx row 33. Error exists in NPCI source data.
---
