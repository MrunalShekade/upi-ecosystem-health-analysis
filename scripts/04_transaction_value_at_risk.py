import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# ── Assumptions ──────────────────────────────────────────────────────────────
# All assumptions must be documented and defensible in interviews
AVG_TICKET_SIZE_RS = 1576        # RBI published average UPI ticket size FY2024-25
BENCHMARK_TD_PCT = 0.07          # HDFC Bank - best performer in dataset
INDUSTRY_AVG_TD_PCT = 0.52       # SBI level - large bank average
# ─────────────────────────────────────────────────────────────────────────────

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DB_URL)

# Pull remitter data only - sending side is where bank infrastructure matters most
query = """
    SELECT 
        bank_name,
        year,
        month,
        total_volume_mn,
        td_pct,
        approved_pct
    FROM upi_data
    WHERE file_type = 'remitter'
    ORDER BY bank_name, year, month
"""

df = pd.read_sql(query, engine)
print(f"Loaded {len(df)} rows from PostgreSQL")

# ── Calculate transaction value at risk ──────────────────────────────────────
# Failed transactions in millions
df['failed_volume_mn'] = df['total_volume_mn'] * (df['td_pct'] / 100)

# Transaction value at risk in crores
# 1 Mn transactions × avg ticket size / 10 million = crores
df['value_at_risk_crores'] = df['failed_volume_mn'] * AVG_TICKET_SIZE_RS / 10

# ── Bank level summary ───────────────────────────────────────────────────────
bank_summary = df.groupby('bank_name').agg(
    total_volume_mn=('total_volume_mn', 'sum'),
    total_failed_mn=('failed_volume_mn', 'sum'),
    total_value_at_risk_crores=('value_at_risk_crores', 'sum'),
    months_present=('month', 'count')
).reset_index()

# Weighted TD%
bank_summary['weighted_td_pct'] = (
    bank_summary['total_failed_mn'] / bank_summary['total_volume_mn'] * 100
).round(2)

bank_summary = bank_summary[bank_summary['months_present'] >= 12]
bank_summary = bank_summary.sort_values('total_value_at_risk_crores', ascending=False)
bank_summary['total_value_at_risk_crores'] = bank_summary['total_value_at_risk_crores'].round(2)

# ── Scenario analysis ────────────────────────────────────────────────────────
# What if every bank matched HDFC benchmark of 0.07% TD%?
bank_summary['benchmark_failed_mn'] = (
    bank_summary['total_volume_mn'] * (BENCHMARK_TD_PCT / 100)
)
bank_summary['benchmark_value_at_risk_crores'] = (
    bank_summary['benchmark_failed_mn'] * AVG_TICKET_SIZE_RS / 10
).round(2)

bank_summary['avoidable_value_at_risk_crores'] = (
    bank_summary['total_value_at_risk_crores'] - 
    bank_summary['benchmark_value_at_risk_crores']
).round(2)

# ── Ecosystem totals ─────────────────────────────────────────────────────────
total_at_risk = bank_summary['total_value_at_risk_crores'].sum()
total_avoidable = bank_summary['avoidable_value_at_risk_crores'].sum()
total_volume = bank_summary['total_volume_mn'].sum()

print(f"\n{'='*60}")
print(f"ECOSYSTEM TRANSACTION VALUE AT RISK SUMMARY")
print(f"{'='*60}")
print(f"Total transaction volume analysed:  {total_volume:,.0f} Mn")
print(f"Total value at risk:                ₹{total_at_risk:,.0f} Crores")
print(f"Avoidable value at risk(vs HDFC bench):  ₹{total_avoidable:,.0f} Crores")
print(f"Avg ticket size assumption:         ₹{AVG_TICKET_SIZE_RS}")
print(f"Benchmark TD% (HDFC):               {BENCHMARK_TD_PCT}%")
print(f"{'='*60}")

print(f"\nTop 10 banks by transaction value at risk:")
print(bank_summary[['bank_name', 'weighted_td_pct', 'total_volume_mn', 
                      'total_value_at_risk_crores', 
                      'avoidable_value_at_risk_crores']].head(10).to_string(index=False))

# ── Save results ─────────────────────────────────────────────────────────────
OUTPUT_PATH = r"C:\Projects\upi-analysis\data\processed\transaction_value_at_risk.csv"
bank_summary.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved to {OUTPUT_PATH}")
