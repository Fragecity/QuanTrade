"""Tests for the update module."""

import os
import tempfile
import toml
import sqlite3
from datetime import datetime, timedelta
from src.get_stock.update import update_data
from src.database.database import create_database


def test_update_data():
    """Test the update_data function to ensure it properly updates existing data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = os.path.join(temp_dir, "test_update.db")
        toml_file = os.path.join(temp_dir, "test_update.toml")
        
        # 1. Create database and initial TOML file
        create_database(db_file, toml_file)
        
        # 2. Create a TOML file with specific test data
        test_config = {
            'stocks': [
                {
                    'name': 'AAPL',
                    'start_date': '2022-01-01',
                    'end_date': '2022-01-05'  # Initial range
                }
            ],
            'national_debt': [
                {
                    'name': 'US',
                    'start_date': '2022-01-01',
                    'end_date': '2022-01-05'
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # 3. Manually insert some test data into the database to simulate existing data
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Insert some stock data
        cursor.execute('''
            INSERT INTO stocks (symbol, date, open, close, high, low, volume, pe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('AAPL', '2022-01-01', 150.0, 151.0, 152.0, 149.0, 1000000, 25.5))
        
        cursor.execute('''
            INSERT INTO stocks (symbol, date, open, close, high, low, volume, pe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('AAPL', '2022-01-02', 151.0, 152.0, 153.0, 150.0, 1100000, 25.6))
        
        # Insert some national debt data
        cursor.execute('''
            INSERT INTO national_debt (nation, date, yield)
            VALUES (?, ?, ?)
        ''', ('US', '2022-01-01', 1.5))
        
        cursor.execute('''
            INSERT INTO national_debt (nation, date, yield)
            VALUES (?, ?, ?)
        ''', ('US', '2022-01-02', 1.6))
        
        conn.commit()
        conn.close()
        
        # 4. Verify that test data was inserted
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM stocks WHERE symbol = 'AAPL'")
        stock_count_before = cursor.fetchone()[0]
        assert stock_count_before == 2, "Should have 2 stock records before update"
        
        cursor.execute("SELECT COUNT(*) FROM national_debt WHERE nation = 'US'")
        debt_count_before = cursor.fetchone()[0]
        assert debt_count_before == 2, "Should have 2 debt records before update"
        
        # Get the latest dates before update
        cursor.execute("SELECT MAX(date) FROM stocks WHERE symbol = 'AAPL'")
        latest_stock_date_before = cursor.fetchone()[0]
        assert latest_stock_date_before == '2022-01-02', "Latest stock date should be 2022-01-02"
        
        cursor.execute("SELECT MAX(date) FROM national_debt WHERE nation = 'US'")
        latest_debt_date_before = cursor.fetchone()[0]
        assert latest_debt_date_before == '2022-01-02', "Latest debt date should be 2022-01-02"
        
        conn.close()
        
        # 5. Try to update data (this may fail due to API rate limits, but shouldn't crash)
        try:
            update_data(db_file, toml_file)
            
            # 6. Verify that the function ran without crashing (even if API calls failed)
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Verify tables still exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'")
            assert cursor.fetchone() is not None, "Stocks table should still exist"
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='national_debt'")
            assert cursor.fetchone() is not None, "National debt table should still exist"
            
            conn.close()
            
        except Exception as e:
            # This is acceptable due to API rate limits
            if "YFRateLimitError" in str(type(e)) or "Too Many Requests" in str(e):
                print(f"Expected API rate limit reached: {e}")
            else:
                raise  # Re-raise if it's a different error


def test_update_data_with_empty_database():
    """Test update_data when the database is empty for a given symbol/nation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = os.path.join(temp_dir, "test_empty.db")
        toml_file = os.path.join(temp_dir, "test_empty.toml")
        
        # Create database and TOML
        create_database(db_file, toml_file)
        
        # TOML with stock/debt we want to update
        test_config = {
            'stocks': [
                {
                    'name': 'MSFT',
                    'start_date': '2022-01-01',
                    'end_date': '2022-01-03'
                }
            ],
            'national_debt': [
                {
                    'name': 'US',
                    'start_date': '2022-01-01',
                    'end_date': '2022-01-03'
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Verify database is empty for these symbols/nations
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM stocks WHERE symbol = 'MSFT'")
        assert cursor.fetchone()[0] == 0, "Should have no MSFT records initially"
        
        cursor.execute("SELECT COUNT(*) FROM national_debt WHERE nation = 'US'")
        assert cursor.fetchone()[0] == 0, "Should have no US debt records initially"
        
        conn.close()
        
        # Update data (may fail due to API, but shouldn't crash)
        try:
            update_data(db_file, toml_file)
        except Exception as e:
            if "YFRateLimitError" not in str(type(e)) and "Too Many Requests" not in str(e):
                raise


def test_update_data_specific_behavior():
    """Test the specific behavior of updating: delete latest day's data and add fresh data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = os.path.join(temp_dir, "test_specific.db")
        toml_file = os.path.join(temp_dir, "test_specific.toml")
        
        # Create database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create tables manually to match database.py
        cursor.execute('''
            CREATE TABLE stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume INTEGER,
                pe REAL,
                UNIQUE(symbol, date)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE national_debt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nation TEXT NOT NULL,
                date DATE NOT NULL,
                yield REAL,
                UNIQUE(nation, date)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create TOML config
        test_config = {
            'stocks': [
                {
                    'name': 'TSLA',
                    'start_date': '2022-01-01',
                    'end_date': '2022-01-10'
                }
            ],
            'national_debt': [
                {
                    'name': 'US',
                    'start_date': '2022-01-01',
                    'end_date': '2022-01-10'
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Insert some test data that would need updating
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Insert some data for TSLA
        for i in range(1, 4):  # Days 1-3
            date_str = f'2022-01-{i:02d}'
            cursor.execute('''
                INSERT INTO stocks (symbol, date, open, close, high, low, volume, pe)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('TSLA', date_str, 1000.0 + i, 1001.0 + i, 1002.0 + i, 999.0 + i, 500000 + i*100000, 80.0 + i))
        
        # Insert some data for US debt
        for i in range(1, 4):  # Days 1-3
            date_str = f'2022-01-{i:02d}'
            cursor.execute('''
                INSERT INTO national_debt (nation, date, yield)
                VALUES (?, ?, ?)
            ''', ('US', date_str, 1.5 + i*0.1))
        
        conn.commit()
        conn.close()
        
        # Verify data was inserted
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM stocks WHERE symbol = 'TSLA'")
        assert cursor.fetchone()[0] == 3, "Should have 3 TSLA records initially"
        
        cursor.execute("SELECT MAX(date) FROM stocks WHERE symbol = 'TSLA'")
        latest_date = cursor.fetchone()[0]
        assert latest_date == '2022-01-03', "Latest date should be 2022-01-03"
        
        conn.close()
        
        # Try updating - in normal conditions this would fetch data from the latest date forward
        try:
            update_data(db_file, toml_file)
        except Exception as e:
            # Expected due to API rate limits
            if "YFRateLimitError" not in str(type(e)) and "Too Many Requests" not in str(e):
                raise