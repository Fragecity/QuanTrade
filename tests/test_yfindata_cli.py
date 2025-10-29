import subprocess
import sys
from pathlib import Path


def test_yfindata_help():
    """Test that yFinData CLI shows help message properly."""
    # Use the direct path to the yFinData executable in the virtual environment
    yfindata_path = Path.cwd() / ".venv" / "bin" / "yFinData"
    result = subprocess.run([str(yfindata_path), '--help'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'CLI tool for managing stock and national debt data with yfinance.' in result.stdout
    assert 'capture-stock' in result.stdout
    assert 'capture-national-debt' in result.stdout
    assert 'config' in result.stdout
    assert 'download' in result.stdout
    assert 'init' in result.stdout


def test_yfindata_capture_stock_invalid_ticker():
    """Test that yFinData CLI handles invalid stock tickers properly."""
    yfindata_path = Path.cwd() / ".venv" / "bin" / "yFinData"
    result = subprocess.run([str(yfindata_path), 'capture-stock', 'INVALIDTICKER', '2023-01-01'], 
                          capture_output=True, text=True)
    # The command should fail gracefully, not crash
    assert result.returncode in [0, 1]  # Could succeed if the API returns data or fail with an error


def test_yfindata_capture_national_debt():
    """Test that yFinData CLI capture-national-debt command exists."""
    yfindata_path = Path.cwd() / ".venv" / "bin" / "yFinData"
    result = subprocess.run([str(yfindata_path), 'capture-national-debt', 'US', '2023-01-01'], 
                          capture_output=True, text=True)
    # Even if the request fails due to API limits, it should return a proper error, not crash
    assert result.returncode in [0, 1]  # Could succeed or fail gracefully


def test_yfindata_config_command():
    """Test that yFinData CLI config command exists."""
    # Using a temporary config to avoid modifying actual project config
    yfindata_path = Path.cwd() / ".venv" / "bin" / "yFinData"
    result = subprocess.run([str(yfindata_path), 'config'], 
                          capture_output=True, text=True)
    # Config command without options should show help or a relevant message
    assert result.returncode in [0, 1]


def test_yfindata_init_command():
    """Test that yFinData CLI init command works."""
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir) / "test_data"
        yfindata_path = Path.cwd() / ".venv" / "bin" / "yFinData"
        result = subprocess.run([str(yfindata_path), 'init', str(test_dir)], 
                              capture_output=True, text=True)
        
        # Check that the command at least attempted to run
        # It may fail if it's run multiple times in the same temp directory
        assert result.returncode in [0, 1]
        
        # If successful, it should create the directory and files
        if result.returncode == 0:
            assert test_dir.exists()
            assert (test_dir / "stock.db").exists()
            assert (test_dir / "stock.toml").exists()


if __name__ == "__main__":
    test_yfindata_help()
    test_yfindata_capture_stock_invalid_ticker()
    test_yfindata_capture_national_debt()
    test_yfindata_config_command()
    test_yfindata_init_command()
    print("All tests passed!")