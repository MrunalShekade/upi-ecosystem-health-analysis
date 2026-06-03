# UPI Ecosystem Health Analysis

An end-to-end data analysis project examining the health of India's UPI payment ecosystem across 82 banks from January 2024 to February 2026, using data published by NPCI.

**Author:** Mrunal Shekade - [GitHub](https://github.com/MrunalShekade)

---

## Project Overview

This project analyses transaction success rates, failure patterns, and transaction value at risk across Indian banks participating in UPI. The dataset covers 2,479 rows of monthly remitter and beneficiary performance data across 82 standardised bank entities, sourced from 52 NPCI Excel files.

The analysis identifies which banks are dragging down ecosystem reliability, quantifies the financial impact of failures, and surfaces the key insight that ecosystem wide decline is driven by user behaviour (BD%) rather than bank infrastructure (TD%).

---

## Key Findings

1. **RRB Infrastructure Crisis** - All top worst performers are Regional Rural Banks undergoing government-mandated One State One RRB mergers. UP Gramin Bank leads with 5.58% weighted TD%.

2. **UP Gramin Bank - Spike, Recovery, Regression** - TD% peaked at 36.31% in Jan 2024, recovered to 0.28% by Sep 2024, then spiked again to 10.22% in Sep 2025 following the May 2025 merger.

3. **India Post Volume Risk** - 1.21% TD% sounds acceptable, but India Post handles 13,158 Mn transactions - the highest absolute failure volume in the dataset.

4. **Remitter Worse Than Beneficiary** - Banks consistently perform worse sending money than receiving it, suggesting outgoing processing infrastructure is the weak point.

5. **Ecosystem Success Rate Declining** - Approved% dropped from 94.38% in Jan 2024 to 90.54% in Feb 2026. The driver is BD% doubling from 4.86% to 9.26%,a user behaviour problem, not a bank infrastructure problem.

6. **Banks Bad at Both Roles** - UP Gramin Bank, Andhra Pradesh Grameena Bank, Karnataka Grameena Bank, Maharashtra Gramin Bank, and Rajasthan Gramin Bank all perform poorly as both remitter and beneficiary.

7. **Scale Brings Reliability** - Perfect inverse relationship: high volume banks average 0.38% TD% vs 1.90% for low volume banks.

8. **NSDL Asymmetry** - 2.92% TD% as remitter but only 0.78% as beneficiary. Specifically weak at sending money.

9. **Transaction Value at Risk** - Total value at risk across the ecosystem: ₹3,31,454 Crores. Recoverable vs HDFC benchmark: ₹2,80,859 Crores. Note: this is value at risk, not revenue lost - customers often retry.

10. **HDFC Benchmark** - 0.07% TD% with 36,122 Mn volume. The industry gold standard used as benchmark throughout.

---

## Tech Stack

| Tool                      | Purpose                          |
|---------------------------|----------------------------------|
| Python (pandas, openpyxl) | Data cleaning and transformation |
| PostgreSQL                | Data storage and SQL analysis    |
| SQLAlchemy + psycopg2     | Python to PostgreSQL connection  |
| Power BI                  | Interactive dashboard            |
| pytest                    | Data quality validation          |

---

## Project Structure

```
upi-analysis/
├── data/
│   ├── raw/                    52 original NPCI Excel files
│   └── processed/
│       ├── bank_master.csv     165 raw → 82 standard bank mappings
│       ├── unique_banks.csv
│       └── transaction_value_at_risk.csv
├── docs/
│   ├── findings.md             10 analytical findings
│   ├── data_quality_notes.md   13 documented issues and fixes
│   └── glossary.md
├── scripts/
│   ├── 01_load_raw.py          Raw file exploration
│   ├── 02_extract_banks.py     Extract unique bank names
│   ├── 03_clean_and_load.py    Clean 52 files, load to PostgreSQL
│   └── 04_transaction_value_at_risk.py    Transaction value at risk model
├── sql/
│   ├── 01_bank_rankings.sql    Volume-weighted TD% rankings
│   ├── 02_trend_analysis.sql   Monthly trend with 3m rolling average
│   ├── 03_remitter_vs_beneficiary.sql
│   ├── 04_ecosystem_trend.sql  Ecosystem-wide success rate
│   ├── 05_volume_vs_failure.sql
│   └── 06_transaction_value_at_risk.sql
├── tests/
│   └── test_data_quality.py    7/7 tests passing
├── .env                        DB credentials (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Database Schema

**Table:** `public.upi_data` — 2,479 rows

| Column           | Type   |           Description             |
|------------------|--------|-----------------------------------|
| bank_name        | TEXT   | Standardised bank name            |
| file_type        | TEXT   | remitter or beneficiary           |
| year             | BIGINT | Year                              |
| month            | BIGINT | Month (1-12)                      |
| total_volume_mn  | FLOAT  | Transaction volume in millions    |
| approved_pct     | FLOAT  | Approval rate (0-100 scale)       |
| bd_pct           | FLOAT  | Business decline % (0-100 scale)  |
| td_pct           | FLOAT  | Technical decline % (0-100 scale) |

---

## Key Assumptions

| Assumption              |       Value         |          Source            |
|-------------------------|---------------------|----------------------------|
| Average UPI ticket size | ₹1,576              | RBI FY2024-25              |
| Benchmark TD%           | 0.07%               | HDFC Bank (best performer) |
| Analysis period         | Jan 2024 – Feb 2026 | NPCI published data        |

**Important:** Transaction value at risk ≠ revenue lost. Customers often retry failed transactions and money does not leave the account on a technical decline. This metric represents the value of transactions exposed to failure risk.

---

## Data Quality

13 data quality issues were identified and resolved during the cleaning process. Key issues include:

- 165 raw bank name variations standardised to 82 entities
- Percentage scale error in NPCI source data (Jan-Jul 2025) corrected
- 34 duplicate rows from RRB merger mappings resolved via volume-weighted aggregation
- 1 impossible value (124.22% approved rate) set to NULL

Full documentation: [`docs/data_quality_notes.md`](docs/data_quality_notes.md)

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Power BI Desktop

### Installation

```bash
git clone https://github.com/MrunalShekade/upi-analysis.git
cd upi-analysis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=upi_analysis
DB_USER=your_user
DB_PASSWORD=your_password
```

### Running the Pipeline

```bash
# Step 1: Explore raw files
python scripts/01_load_raw.py

# Step 2: Extract bank names
python scripts/02_extract_banks.py

# Step 3: Clean and load to PostgreSQL
python scripts/03_clean_and_load.py

# Step 4: Calculate transaction value at risk
python scripts/04_revenue_impact.py

# Run tests
pytest tests/
```

---

## Data Source

All data sourced from NPCI (National Payments Corporation of India) monthly UPI performance reports, publicly available at [npci.org.in](https://www.npci.org.in).
