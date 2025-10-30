"""
Unit tests for the add CLI command in yFinData.
"""

import os
import tempfile
import shutil
import sqlite3
import toml
import subprocess
from pathlib import Path


def test_add_cli_command_add_new_stock():
    """Test the add CLI command when adding a new stock to the TOML."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Define file paths
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        
        db_file = data_dir / "stock.db"
        toml_file = data_dir / "stock.toml"
        
        # Create a TOML configuration without AAPL
        test_config = {
            "stocks": [
                {
                    "name": "TSLA",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            ],
            "national_debt": [
                {
                    "name": "DGS10",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Create empty database with required tables
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create required tables
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
        
        # Create config directory and file
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        config_file = config_dir / "config.toml"
        config_content = {
            "paths": {
                "toml": str(toml_file),
                "db": str(db_file)
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            toml.dump(config_content, f)
        
        # Change to temp directory and run the add command
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the yFinData add command for a new stock
            result = subprocess.run([
                "uv", "run", "yFinData", "add", "AAPL", "2023-06-01"
            ], capture_output=True, text=True, cwd=temp_dir)
            
            # The command should execute and add the stock to TOML
            print(f"Add command output: {result.stdout}")
            if result.stderr:
                print(f"Add command errors: {result.stderr}")
            
            # Verify that AAPL was added to the TOML
            with open(toml_file, 'r') as f:
                updated_config = toml.load(f)
            
            # Check that AAPL was added to the stocks list
            aapl_found = False
            for stock in updated_config.get('stocks', []):
                if stock['name'] == 'AAPL':
                    aapl_found = True
                    assert stock['start_date'] == '2023-06-01'
                    # Check that end_date is set (should be today's date format)
                    assert 'end_date' in stock
                    break
            
            assert aapl_found, "AAPL should have been added to the TOML"
            
        finally:
            os.chdir(original_cwd)
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def test_add_cli_command_update_existing_stock():
    """Test the add CLI command when updating an existing stock in the TOML."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Define file paths
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        
        db_file = data_dir / "stock.db"
        toml_file = data_dir / "stock.toml"
        
        # Create a TOML configuration with AAPL already present
        test_config = {
            "stocks": [
                {
                    "name": "AAPL",
                    "start_date": "2022-01-01",
                    "end_date": "2022-12-31"
                },
                {
                    "name": "TSLA",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            ],
            "national_debt": [
                {
                    "name": "DGS10",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Create empty database with required tables
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create required tables
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
        
        # Create config directory and file
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        config_file = config_dir / "config.toml"
        config_content = {
            "paths": {
                "toml": str(toml_file),
                "db": str(db_file)
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            toml.dump(config_content, f)
        
        # Change to temp directory and run the add command
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the yFinData add command for an existing stock (should update it)
            result = subprocess.run([
                "uv", "run", "yFinData", "add", "AAPL", "2023-01-01"
            ], capture_output=True, text=True, cwd=temp_dir)
            
            # The command should execute and update the stock in TOML
            print(f"Add command output: {result.stdout}")
            if result.stderr:
                print(f"Add command errors: {result.stderr}")
            
            # Verify that AAPL was updated in the TOML
            with open(toml_file, 'r') as f:
                updated_config = toml.load(f)
            
            # Check that AAPL was updated in the stocks list
            aapl_found = False
            for stock in updated_config.get('stocks', []):
                if stock['name'] == 'AAPL':
                    aapl_found = True
                    assert stock['start_date'] == '2023-01-01', f"Expected start date 2023-01-01, got {stock['start_date']}"
                    # Check that end_date is set (should be today's date format)
                    assert 'end_date' in stock
                    break
            
            assert aapl_found, "AAPL should have been found in the TOML"
            
        finally:
            os.chdir(original_cwd)
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def test_add_cli_command_case_insensitive():
    """Test the add CLI command handles case-insensitively."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Define file paths
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        
        db_file = data_dir / "stock.db"
        toml_file = data_dir / "stock.toml"
        
        # Create a TOML configuration with AAPL in uppercase
        test_config = {
            "stocks": [
                {
                    "name": "AAPL",
                    "start_date": "2022-01-01",
                    "end_date": "2022-12-31"
                }
            ],
            "national_debt": [
                {
                    "name": "DGS10",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31"
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Create empty database with required tables
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create required tables
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
        
        # Create config directory and file
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir()
        
        config_file = config_dir / "config.toml"
        config_content = {
            "paths": {
                "toml": str(toml_file),
                "db": str(db_file)
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            toml.dump(config_content, f)
        
        # Change to temp directory and run the add command with lowercase
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the yFinData add command for aapl (lowercase) - should update the existing AAPL
            result = subprocess.run([
                "uv", "run", "yFinData", "add", "aapl", "2023-01-01"
            ], capture_output=True, text=True, cwd=temp_dir)
            
            # The command should execute and update the existing AAPL stock (case-insensitively)
            print(f"Add command output: {result.stdout}")
            if result.stderr:
                print(f"Add command errors: {result.stderr}")
            
            # Verify that AAPL was updated in the TOML (still uppercase in the file)
            with open(toml_file, 'r') as f:
                updated_config = toml.load(f)
            
            # Check that AAPL was updated in the stocks list
            aapl_found = False
            for stock in updated_config.get('stocks', []):
                if stock['name'] == 'AAPL':  # Should still be stored as uppercase
                    aapl_found = True
                    assert stock['start_date'] == '2023-01-01', f"Expected start date 2023-01-01, got {stock['start_date']}"
                    # Check that end_date is set
                    assert 'end_date' in stock
                    break
            
            assert aapl_found, "AAPL should have been found and updated in the TOML"
            
        finally:
            os.chdir(original_cwd)
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)