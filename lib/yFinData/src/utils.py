"""
Shared data processing functions for yFinData project.
"""

import sqlite3
import toml
from datetime import datetime
from math import isnan
from typing import Callable, Any
from get_stock.stock_struct import capture_stock, capture_national_debt


def _process_stock_data(config_entry: dict, conn: sqlite3.Connection, 
                       capture_func: Callable = capture_stock):
    """Process a single stock data entry from TOML config."""
    name = config_entry['name']
    start_date_str = config_entry['start_date']
    
    # Parse start date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # Capture stock data
    stock_data = capture_func(name, start_date)
    
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


def _process_national_debt_data(config_entry: dict, conn: sqlite3.Connection,
                               capture_func: Callable = capture_national_debt):
    """Process a single national debt data entry from TOML config."""
    name = config_entry['name']
    start_date_str = config_entry['start_date']
    
    # Parse start date
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # Capture national debt data (treasury yields)
    debt_data = capture_func(name, start_date)
    
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


def process_toml_config(toml_file: str, conn: sqlite3.Connection, 
                      stock_capture_func: Callable = capture_stock,
                      debt_capture_func: Callable = capture_national_debt,
                      stock_preprocess_func: Callable = None,
                      debt_preprocess_func: Callable = None):
    """
    Generic function to process TOML configuration and store data in database.
    
    Args:
        toml_file: Path to the TOML configuration file
        conn: SQLite database connection
        stock_capture_func: Function to capture stock data
        debt_capture_func: Function to capture debt data
        stock_preprocess_func: Optional function to preprocess stock data before insertion
        debt_preprocess_func: Optional function to preprocess debt data before insertion
    """
    # Read the TOML file
    with open(toml_file, 'r', encoding='utf-8') as f:
        config = toml.load(f)
    
    # Process stock entries
    if 'stocks' in config:
        for stock_entry in config['stocks']:
            if stock_preprocess_func:
                # Apply preprocessing if provided
                stock_entry = stock_preprocess_func(stock_entry, conn)
            _process_stock_data(stock_entry, conn, stock_capture_func)
    
    # Process national debt entries
    if 'national_debt' in config:
        for debt_entry in config['national_debt']:
            if debt_preprocess_func:
                # Apply preprocessing if provided
                debt_entry = debt_preprocess_func(debt_entry, conn)
            _process_national_debt_data(debt_entry, conn, debt_capture_func)