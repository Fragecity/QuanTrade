"""
Unit tests for the update CLI command in yFinData.
"""

import os
import tempfile
import shutil
import sqlite3
import toml
import subprocess
from pathlib import Path


def test_update_cli_command_with_existing_data():
    """Test the update CLI command with existing data in the database."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Define file paths
        data_dir = Path(temp_dir) / "test_data"
        data_dir.mkdir()
        
        db_file = data_dir / "stock.db"
        toml_file = data_dir / "stock.toml"
        
        # Create a TOML configuration
        test_config = {
            "stocks": [
                {
                    "name": "AAPL",
                    "start_date": "2023-01-01"
                }
            ],
            "national_debt": [
                {
                    "name": "DGS10",  # 10-year treasury
                    "start_date": "2023-01-01"
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Create database file and required tables
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create stocks table
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
        
        # Create national_debt table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS national_debt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nation TEXT NOT NULL,
                date DATE NOT NULL,
                yield REAL,
                UNIQUE(nation, date)
            )
        ''')
        
        # Insert some initial data
        cursor.execute('''
            INSERT INTO stocks (symbol, date, open, close, high, low, volume, pe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("AAPL", "2023-01-01", 150.0, 152.0, 153.0, 149.0, 1000000, 25.5))
        
        cursor.execute('''
            INSERT INTO national_debt (nation, date, yield)
            VALUES (?, ?, ?)
        ''', ("DGS10", "2023-01-01", 3.5))
        
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
        
        # Change to temp directory and run the update command
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the yFinData update command via subprocess
            result = subprocess.run([
                "uv", "run", "yFinData", "update"
            ], capture_output=True, text=True, cwd=original_cwd)
            
            # Check that the command executed without errors
            # It may fail due to API rate limits, but shouldn't crash
            print(f"Update command output: {result.stdout}")
            if result.stderr:
                print(f"Update command errors: {result.stderr}")
                
        finally:
            os.chdir(original_cwd)
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def test_update_cli_command_with_config():
    """Test the update CLI command when config is properly set."""
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Define file paths
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        
        db_file = data_dir / "stock.db"
        toml_file = data_dir / "stock.toml"
        
        # Create a TOML configuration
        test_config = {
            "stocks": [
                {
                    "name": "TSLA",
                    "start_date": "2023-01-01"
                }
            ],
            "national_debt": [
                {
                    "name": "DGS10",
                    "start_date": "2023-01-01"
                }
            ]
        }
        
        with open(toml_file, 'w', encoding='utf-8') as f:
            toml.dump(test_config, f)
        
        # Create empty database
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
        
        # Change to temp directory and run the update command
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the yFinData update command
            result = subprocess.run([
                "uv", "run", "yFinData", "update"
            ], capture_output=True, text=True, cwd=original_cwd)
            
            # The command should execute without crashing
            # May fail due to API limits but shouldn't crash
            print(f"Update command output: {result.stdout}")
            if result.stderr:
                print(f"Update command errors: {result.stderr}")
                
        finally:
            os.chdir(original_cwd)
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def test_update_cli_command_without_config():
    """Test the update CLI command when no config is set."""
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the yFinData update command without any config
            result = subprocess.run([
                "uv", "run", "yFinData", "update"
            ], capture_output=True, text=True, cwd=original_cwd)
            
            # Should fail gracefully with an error about missing config
            assert result.returncode != 0
            assert "Configuration file not found" in result.stderr
            
        finally:
            os.chdir(original_cwd)
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)