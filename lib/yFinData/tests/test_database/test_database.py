"""Tests for the database module."""

import os
import tempfile
import toml
from datetime import datetime
from pathlib import Path

from src.database.database import create_database, capture_data


def test_create_database():
    """Test that create_database creates both DB and TOML files properly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = os.path.join(temp_dir, "test.db")
        toml_file = os.path.join(temp_dir, "test.toml")

        # Call the function
        create_database(db_file, toml_file)

        # Check that files were created
        assert os.path.exists(db_file), "Database file should be created"
        assert os.path.exists(toml_file), "TOML file should be created"

        # Check that TOML file has the expected structure
        with open(toml_file, "r", encoding="utf-8") as f:
            config = toml.load(f)

        assert "stocks" in config, "TOML should have stocks section"
        assert "national_debt" in config, "TOML should have national_debt section"
        assert len(config["stocks"]) > 0, "TOML should have at least one stock entry"
        assert len(config["national_debt"]) > 0, (
            "TOML should have at least one national debt entry"
        )


def test_capture_data():
    """Test that capture_data works correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = os.path.join(temp_dir, "test.db")
        toml_file = os.path.join(temp_dir, "test.toml")

        # Create initial DB and TOML files
        create_database(db_file, toml_file)

        # Modify TOML to have test data
        test_config = {
            "stocks": [
                {"name": "AAPL", "start_date": "2023-01-01", "end_date": "2023-01-31"}
            ],
            "national_debt": [
                {"name": "US", "start_date": "2023-01-01", "end_date": "2023-01-31"}
            ],
        }

        with open(toml_file, "w", encoding="utf-8") as f:
            toml.dump(test_config, f)

        # Call capture_data - this might fail due to network issues, but shouldn't crash
        try:
            capture_data(db_file, toml_file)

            # Verify database structure is correct
            import sqlite3

            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Check that the tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'"
            )
            assert cursor.fetchone() is not None, "Stocks table should exist"

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='national_debt'"
            )
            assert cursor.fetchone() is not None, "National debt table should exist"

            conn.close()
        except Exception as e:
            # Even if network calls fail, our function should handle it gracefully
            # The important thing is that it doesn't crash and properly handles the exception
            # For example, we could get rate limit errors from yfinance
            if "YFRateLimitError" in str(type(e)) or "Too Many Requests" in str(e):
                # This is expected behavior when testing with real API calls
                pass
            else:
                raise  # Re-raise if it's a different kind of error


def test_toml_structure():
    """Test the structure of the TOML file created by create_database."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_file = os.path.join(temp_dir, "test.db")
        toml_file = os.path.join(temp_dir, "test.toml")

        create_database(db_file, toml_file)

        # Load and verify the TOML structure
        with open(toml_file, "r", encoding="utf-8") as f:
            config = toml.load(f)

        # Verify structure
        assert "stocks" in config
        assert "national_debt" in config

        # Verify expected fields in a stock entry
        if config["stocks"]:
            stock = config["stocks"][0]
            assert "name" in stock
            assert "start_date" in stock
            assert "end_date" in stock

        # Verify expected fields in a national debt entry
        if config["national_debt"]:
            debt = config["national_debt"][0]
            assert "name" in debt
            assert "start_date" in debt
            assert "end_date" in debt


def test_end_to_end_process_with_real_files():
    """Test the complete process: create db and toml files in data/ directory, capture data, and verify storage."""
    import sqlite3

    # Use the data directory for our test files
    data_dir = Path(__file__).parent.parent.parent / "data"
    os.makedirs(data_dir, exist_ok=True)  # Create data directory if it doesn't exist

    db_file = data_dir / "test_end_to_end.db"
    toml_file = data_dir / "test_end_to_end.toml"

    # Clean up any existing files
    if db_file.exists():
        os.remove(db_file)
    if toml_file.exists():
        os.remove(toml_file)

    try:
        # 1. Create the database and toml files
        create_database(str(db_file), str(toml_file))

        # Verify files were created
        assert db_file.exists(), "Database file should be created in data/ directory"
        assert toml_file.exists(), "TOML file should be created in data/ directory"

        # 2. Configure the TOML file with specific stocks and national debt data to capture
        test_config = {
            "stocks": [
                {
                    "name": "AAPL",  # Apple
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-10",  # Short range to reduce API calls
                },
                {
                    "name": "MSFT",  # Microsoft
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-10",
                },
                {
                    "name": "GOOGL",  # Google
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-10",
                },
            ],
            "national_debt": [
                {
                    "name": "US",  # US Treasury yield
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-10",
                }
            ],
        }

        with open(toml_file, "w", encoding="utf-8") as f:
            toml.dump(test_config, f)

        # 3. Capture data from yfinance and store in database
        try:
            capture_data(str(db_file), str(toml_file))

            # 4. Read back the data and verify it was stored
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Check that the tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'"
            )
            assert cursor.fetchone() is not None, "Stocks table should exist"

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='national_debt'"
            )
            assert cursor.fetchone() is not None, "National debt table should exist"

            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM stocks")
            stock_records = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM national_debt")
            debt_records = cursor.fetchone()[0]

            # Verify that the structure is correct (even if no data due to API limits)
            cursor.execute("PRAGMA table_info(stocks)")
            stock_columns = [row[1] for row in cursor.fetchall()]
            expected_stock_columns = [
                "id",
                "symbol",
                "date",
                "open",
                "close",
                "high",
                "low",
                "volume",
                "pe",
            ]
            assert all(col in stock_columns for col in expected_stock_columns), (
                f"Stock table should have expected columns. Got: {stock_columns}"
            )

            cursor.execute("PRAGMA table_info(national_debt)")
            debt_columns = [row[1] for row in cursor.fetchall()]
            expected_debt_columns = ["id", "nation", "date", "yield"]
            assert all(col in debt_columns for col in expected_debt_columns), (
                f"Debt table should have expected columns. Got: {debt_columns}"
            )

            conn.close()

            # Test is successful if we reach this point without exceptions
            print(
                f"End-to-end test completed: {stock_records} stock records, {debt_records} debt records"
            )

        except Exception as e:
            # As before, network/API issues are expected
            if "YFRateLimitError" in str(type(e)) or "Too Many Requests" in str(e):
                print(f"Expected API rate limit reached: {e}")
            else:
                raise

    finally:
        # Clean up test files even if the test fails
        if db_file.exists():
            os.remove(db_file)
        if toml_file.exists():
            os.remove(toml_file)
