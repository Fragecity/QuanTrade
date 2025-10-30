"""
Module to update existing market data in the database to the latest available data.
"""

import sqlite3
from datetime import datetime, timedelta
from math import isnan
from utils import process_toml_config
from .stock_struct import capture_stock, capture_national_debt


def _update_stock_preprocess(stock_entry: dict, conn):
    """Preprocess stock entry for update: find latest date and delete it."""
    name = stock_entry['name']
    cursor = conn.cursor()
    
    # Find the latest date in the database for this stock
    cursor.execute('''
        SELECT MAX(date) FROM stocks 
        WHERE symbol = ?
    ''', (name,))
    result = cursor.fetchone()
    
    if result and result[0] is not None:
        # Get the latest date for this stock in the database
        latest_date_str = result[0]
        latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
        
        # Delete data from the latest date (to handle potential data updates)
        cursor.execute('''
            DELETE FROM stocks 
            WHERE symbol = ? AND date = ?
        ''', (name, latest_date_str))
        
        # Update the start_date to be the latest date we just deleted
        stock_entry = stock_entry.copy()  # Don't modify original
        stock_entry['start_date'] = latest_date_str
        
    cursor.close()
    return stock_entry


def _update_debt_preprocess(debt_entry: dict, conn):
    """Preprocess debt entry for update: find latest date and delete it."""
    name = debt_entry['name']
    cursor = conn.cursor()
    
    # Find the latest date in the database for this nation
    cursor.execute('''
        SELECT MAX(date) FROM national_debt 
        WHERE nation = ?
    ''', (name,))
    result = cursor.fetchone()
    
    if result and result[0] is not None:
        # Get the latest date for this nation in the database
        latest_date_str = result[0]
        latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
        
        # Delete data from the latest date (to handle potential data updates)
        cursor.execute('''
            DELETE FROM national_debt 
            WHERE nation = ? AND date = ?
        ''', (name, latest_date_str))
        
        # Update the start_date to be the latest date we just deleted
        debt_entry = debt_entry.copy()  # Don't modify original
        debt_entry['start_date'] = latest_date_str
        
    cursor.close()
    return debt_entry


def _get_missing_date_ranges_stock(symbol: str, conn) -> list:
    """
    Get missing date ranges for a stock in the database.
    
    Args:
        symbol: Stock symbol to check
        conn: SQLite database connection
        
    Returns:
        List of tuples containing (start_date, end_date) for missing date ranges
    """
    cursor = conn.cursor()
    
    # Get all dates for this stock, ordered by date
    cursor.execute('''
        SELECT date FROM stocks 
        WHERE symbol = ?
        ORDER BY date ASC
    ''', (symbol,))
    
    rows = cursor.fetchall()
    if not rows:
        return []
    
    # Convert to datetime objects
    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in rows]
    
    missing_ranges = []
    for i in range(len(dates) - 1):
        current_date = dates[i]
        next_date = dates[i + 1]
        
        # Check if there are missing days between consecutive dates
        if (next_date - current_date).days > 1:
            # Found a gap, add the missing range
            start_missing = current_date + timedelta(days=1)
            end_missing = next_date - timedelta(days=1)
            missing_ranges.append((start_missing.strftime("%Y-%m-%d"), end_missing.strftime("%Y-%m-%d")))
    
    return missing_ranges


def _get_missing_date_ranges_debt(nation: str, conn) -> list:
    """
    Get missing date ranges for a nation's debt data in the database.
    
    Args:
        nation: Nation name to check
        conn: SQLite database connection
        
    Returns:
        List of tuples containing (start_date, end_date) for missing date ranges
    """
    cursor = conn.cursor()
    
    # Get all dates for this nation, ordered by date
    cursor.execute('''
        SELECT date FROM national_debt 
        WHERE nation = ?
        ORDER BY date ASC
    ''', (nation,))
    
    rows = cursor.fetchall()
    if not rows:
        return []
    
    # Convert to datetime objects
    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in rows]
    
    missing_ranges = []
    for i in range(len(dates) - 1):
        current_date = dates[i]
        next_date = dates[i + 1]
        
        # Check if there are missing days between consecutive dates
        if (next_date - current_date).days > 1:
            # Found a gap, add the missing range
            start_missing = current_date + timedelta(days=1)
            end_missing = next_date - timedelta(days=1)
            missing_ranges.append((start_missing.strftime("%Y-%m-%d"), end_missing.strftime("%Y-%m-%d")))
    
    return missing_ranges


def update_missing_data(db_file: str, toml_file: str):
    """
    Efficiently update existing market data in the database by downloading data 
    from the latest date in the database to the present (today).
    
    For each entry in the TOML file:
    1. Find the latest date in the database for that symbol/nation
    2. Fetch new data from that date to today
    3. Insert the new data into the database
    
    Args:
        db_file: Path to the SQLite database file
        toml_file: Path to the TOML configuration file
    """
    import toml
    from datetime import datetime
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Read the TOML file
    with open(toml_file, 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    # Process stock entries
    if 'stocks' in config:
        for stock_entry in config['stocks']:
            name = stock_entry['name']
            
            # Find the latest date in the database for this stock
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(date) FROM stocks 
                WHERE symbol = ?
            ''', (name,))
            result = cursor.fetchone()
            
            latest_date_str = None
            if result and result[0] is not None:
                latest_date_str = result[0]
            
            cursor.close()
            
            if latest_date_str:
                # Fetch data from the day after the latest date in the database
                start_date = datetime.strptime(latest_date_str, "%Y-%m-%d") + timedelta(days=1)
                stock_data = capture_stock(name, start_date)
                
                # Insert stock data into database
                cursor = conn.cursor()
                for date, price in stock_data.data.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO stocks (symbol, date, open, close, high, low, volume, pe)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stock_data.name,
                        date.strftime("%Y-%m-%d"),
                        price.open,
                        price.close,
                        price.high,
                        price.low,
                        price.volume,
                        None if isnan(price.pe) else price.pe  # Check for NaN
                    ))
                cursor.close()
    
    # Process national debt entries
    if 'national_debt' in config:
        for debt_entry in config['national_debt']:
            name = debt_entry['name']
            
            # Find the latest date in the database for this nation
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(date) FROM national_debt 
                WHERE nation = ?
            ''', (name,))
            result = cursor.fetchone()
            
            latest_date_str = None
            if result and result[0] is not None:
                latest_date_str = result[0]
            
            cursor.close()
            
            if latest_date_str:
                # Fetch data from the day after the latest date in the database
                start_date = datetime.strptime(latest_date_str, "%Y-%m-%d") + timedelta(days=1)
                debt_data = capture_national_debt(name, start_date)
                
                # Insert national debt data into database
                cursor = conn.cursor()
                for date, yield_value in debt_data.data.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO national_debt (nation, date, yield)
                        VALUES (?, ?, ?)
                    ''', (
                        name,
                        date.strftime("%Y-%m-%d"),
                        yield_value
                    ))
                cursor.close()
    
    conn.close()


def update_data(db_file: str, toml_file: str):
    """
    Update existing market data in the database to the latest available data.
    
    For each entry in the TOML file:
    1. Find the latest date in the database for that symbol/nation
    2. Delete data from that latest date
    3. Fetch new data from that date to today
    4. Insert the new data into the database
    
    Args:
        db_file: Path to the SQLite database file
        toml_file: Path to the TOML configuration file
    """
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Process the TOML configuration with update-specific preprocessing
    process_toml_config(
        toml_file, 
        conn, 
        stock_capture_func=capture_stock,
        debt_capture_func=capture_national_debt,
        stock_preprocess_func=_update_stock_preprocess,
        debt_preprocess_func=_update_debt_preprocess
    )
    
    conn.close()