import pandas as pd
import os

RAW_DIR = r"C:\Projects\upi-analysis\data\raw"

files = [f for f in os.listdir(RAW_DIR) if f.endswith('.xlsx') and not f.startswith('~$')]
files.sort()

print(f"Total files found: {len(files)}")
print("\nfirst 5 files: ")
for f in files[:5]:
    print(f)

#preview the first file
first_file = os.path.join(RAW_DIR, files[0])
df = pd.read_excel(first_file, header=1)

print(f"first file: {files[0]}")
print(f"shape: {df.shape}")
print(f"column names: ")
print(df.columns.tolist())
print(f"\nFirst 3 rows:")
print(df.head(3))