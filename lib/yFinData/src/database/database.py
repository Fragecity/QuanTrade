import sqlite3
import toml
from utils import process_toml_config
from constants import DEFAULT_TOML_CONFIG
from get_stock.stock_struct import capture_stock, capture_national_debt


def create_database(db_file: str, toml_file: str):
    """
    Create an empty database file and an empty TOML file.
    
    Args:
        db_file: Path to the SQLite database file to create
        toml_file: Path to the TOML configuration file to create
    """
    # Create empty SQLite database with required tables
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create table for stock data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
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
    
    # Create table for national debt data (treasury yields)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS national_debt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nation TEXT NOT NULL,
            date DATE NOT NULL,
            yield REAL,
            UNIQUE(nation, date)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Create empty TOML file with template structure
    with open(toml_file, 'w', encoding='utf-8') as f:
        toml.dump(DEFAULT_TOML_CONFIG, f)


def capture_data(db_file: str, toml_file: str):
    """
    Capture data from the TOML configuration file and store it in the database.
    
    Args:
        db_file: Path to the SQLite database file
        toml_file: Path to the TOML configuration file
    """
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Process the TOML configuration directly (no preprocessing needed for capture)
    process_toml_config(
        toml_file, 
        conn, 
        stock_capture_func=capture_stock,
        debt_capture_func=capture_national_debt
    )
    
    conn.close()
