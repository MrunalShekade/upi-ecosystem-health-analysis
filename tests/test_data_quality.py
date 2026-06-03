import pytest
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

@pytest.fixture(scope='session')
def db_data():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM upi_data", engine)
    return df

def test_row_count(db_data):
    """Database should have at least 2400 rows"""
    assert len(db_data) >= 2400, f"Expected 2400+ rows, got {len(db_data)}"

def test_no_duplicate_rows(db_data):
    """No duplicate bank/file_type/year/month combinations"""
    dupes = db_data.duplicated(
        subset=['bank_name', 'file_type', 'year', 'month']
    ).sum()
    assert dupes == 0, f"Found {dupes} duplicate rows"

def test_percentage_scale(db_data):
    """All percentage values should be between 0 and 100"""
    for col in ['approved_pct', 'bd_pct', 'td_pct']:
        assert db_data[col].between(0, 100).all(), \
            f"{col} has values outside 0-100 range"

def test_percentage_scale(db_data):
    """All percentage values should be between 0 and 100"""
    for col in ['approved_pct', 'bd_pct', 'td_pct']:
        clean = db_data[col].dropna()
        assert clean.between(0, 100).all(), \
            f"{col} has values outside 0-100 range"

def test_no_null_bank_names(db_data):
    """No null bank names in database"""
    nulls = db_data['bank_name'].isna().sum()
    assert nulls == 0, f"Found {nulls} null bank names"

def test_file_types_valid(db_data):
    """file_type should only be remitter or beneficiary"""
    valid_types = {'remitter', 'beneficiary'}
    actual_types = set(db_data['file_type'].unique())
    assert actual_types == valid_types, \
        f"Unexpected file types: {actual_types - valid_types}"

def test_volume_positive(db_data):
    """All transaction volumes should be positive"""
    assert (db_data['total_volume_mn'] > 0).all(), \
        "Found zero or negative transaction volumes"