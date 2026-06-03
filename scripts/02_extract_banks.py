import pandas as pd
import os

RAW_DIR = r"C:\Projects\upi-analysis\data\raw"
OUTPUT_DIR = r"C:\Projects\upi-analysis\data\processed"

files = [f for f in os.listdir(RAW_DIR) if f.endswith('.xlsx') and not f.startswith('~$')]
files.sort()

all_banks = []

for filename in files:
    filepath = os.path.join(RAW_DIR, filename)
    #skip the title row that npci adds at the top of every excel file
    df = pd.read_excel(filepath, header=1)

    bank_column = df.iloc[:,1] #always column index 1 regardless of header name
    file_type = 'remitter' if 'remitter' in filename else 'beneficiary'

    for bank in bank_column:
        all_banks.append({
            'bank_name' : bank,
            'file_type' : file_type,
            'source_file' : filename
        })

result = pd.DataFrame(all_banks)
result = result.dropna(subset=['bank_name'])
result = result.drop_duplicates(subset=['bank_name','file_type'])
result = result.sort_values('bank_name')

result.to_csv(os.path.join(OUTPUT_DIR, 'unique_banks.csv'), index=False)
print((f"Total unique bank-type combinations: {len(result)}"))
print(f"Sample:",result.head(10))