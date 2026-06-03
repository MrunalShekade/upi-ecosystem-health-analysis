import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = r"C:\Projects\upi-analysis\data\raw"
MASTER_FILE = r"C:\Projects\upi-analysis\data\processed\bank_master.csv"

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

#load bank master lookup table
bank_master = pd.read_csv(MASTER_FILE)
master_lookup = dict(zip(bank_master['raw_name'], bank_master['standard_name']))

def standardise_columns(df, file_type):
    if file_type == 'beneficiary':
        df.columns = ['sr_no', 'bank_name_raw', 'total_volume_mn',
                      'approved_pct', 'bd_pct', 'td_pct', 
                      'deemed_approved'][:len(df.columns)]
    else:  # remitter
        df.columns = ['sr_no', 'bank_name_raw', 'total_volume_mn',
                      'approved_pct', 'bd_pct', 'td_pct',
                      'debit_reversal_count', 
                      'debit_reversal_success_pct'][:len(df.columns)]
    
    cols_to_keep = ['bank_name_raw', 'total_volume_mn', 'approved_pct', 'bd_pct', 'td_pct']
    df = df[cols_to_keep]
    
    return df

def clean_dataframe(df, file_type, year, month):
    #apply bank name standardization from master lookup
    df['bank_name'] = df['bank_name_raw'].map(master_lookup)
    #drop excluded banks and unmatched names
    df = df[df['bank_name'].notna()]
    df = df[df['bank_name'] != 'EXCLUDE']

    #convert volume, remove commas and convert to float
    df['total_volume_mn'] = df['total_volume_mn'].astype(str).str.replace(',', '').str.strip()
    df['total_volume_mn'] = pd.to_numeric(df['total_volume_mn'], errors='coerce')
   
    # Convert percentage columns, remove % and convert to float
    for col in ['approved_pct', 'bd_pct', 'td_pct']:
        df[col] = df[col].astype(str).str.replace('%', '').str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fix scale issue: Jan-Jul 2025 files stored as decimals (0.9455) 
    # instead of percentages (94.55). Multiply by 100 to normalise.
    if year == 2025 and month <= 7:
        for col in ['approved_pct', 'bd_pct', 'td_pct']:
            df[col] = df[col] * 100
    # Cap impossible values — source data errors where approved_pct > 100
    df.loc[df['approved_pct'] > 100, 'approved_pct'] = np.nan

    #add metadata columns
    df['year'] = year
    df['month'] = month
    df['file_type'] = file_type

    
    # Keep only final columns
    df = df[['bank_name', 'file_type', 'year', 'month', 
             'total_volume_mn', 'approved_pct', 'bd_pct', 'td_pct']]

    # Aggregate duplicate rows caused by pre-merger banks mapping 
    # to same standard name in same month
    df['vol_x_approved'] = df['total_volume_mn'] * df['approved_pct']
    df['vol_x_bd'] = df['total_volume_mn'] * df['bd_pct']
    df['vol_x_td'] = df['total_volume_mn'] * df['td_pct']

    df = df.groupby(['bank_name', 'file_type', 'year', 'month'], as_index=False).agg(
        total_volume_mn=('total_volume_mn', 'sum'),
        vol_x_approved=('vol_x_approved', 'sum'),
        vol_x_bd=('vol_x_bd', 'sum'),
        vol_x_td=('vol_x_td', 'sum')
    )

    df['approved_pct'] = df['vol_x_approved'] / df['total_volume_mn']
    df['bd_pct'] = df['vol_x_bd'] / df['total_volume_mn']
    df['td_pct'] = df['vol_x_td'] / df['total_volume_mn']

    df = df[['bank_name', 'file_type', 'year', 'month', 
             'total_volume_mn', 'approved_pct', 'bd_pct', 'td_pct']]
    
    return df
    

all_dataframes = []

files = [f for f in os.listdir(RAW_DIR) if f.endswith('.xlsx') and not f.startswith('~$')]
files.sort()

for filename in files:
    try:
        # Extract metadata from filename
        parts = filename.replace('.xlsx', '').split('_')
        file_type = parts[1]
        year = int(parts[2])
        month = int(parts[3])
        
        # Read file
        filepath = os.path.join(RAW_DIR, filename)
        df = pd.read_excel(filepath, header=1)
        
        # Clean
        df = standardise_columns(df, file_type)
        df = clean_dataframe(df, file_type, year, month)
        
        all_dataframes.append(df)
        print(f"✓ {filename} — {len(df)} rows")
        
    except Exception as e:
        print(f"✗ {filename} — ERROR: {e}")

# Combine all into one DataFrame
final_df = pd.concat(all_dataframes, ignore_index=True)
print(f"\nTotal rows: {len(final_df)}")
print(final_df.head())

# Load into PostgreSQL
engine = create_engine(DB_URL)
final_df.to_sql('upi_data', engine, if_exists='replace', index=False)
print(f"\nSuccessfully loaded {len(final_df)} rows into PostgreSQL table 'upi_data'")