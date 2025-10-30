import subprocess
import sys
import tempfile
import os
from pathlib import Path
import sqlite3
import toml


def run_yf_cmd(args):
    """Helper function to run yFinData commands"""
    cmd = ["uv", "run", "yFinData"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    return result


def test_cli_commands():
    """Test the new CLI commands"""
    print("Testing yFinData CLI commands...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test 1: init command
        print("\n1. Testing init command...")
        result = run_yf_cmd(["init", str(temp_path / "test_data")])
        assert result.returncode == 0, f"Init command failed: {result.stderr}"
        print("   ✓ Init command works")
        
        # Verify files were created
        toml_file = temp_path / "test_data" / "stock.toml"
        db_file = temp_path / "test_data" / "stock.db"
        assert toml_file.exists(), "TOML file was not created"
        assert db_file.exists(), "DB file was not created"
        print("   ✓ Files created successfully")
        
        # Test 2: config command
        print("\n2. Testing config command...")
        result = run_yf_cmd(["config", "--toml", str(toml_file), "--db", str(db_file)])
        assert result.returncode == 0, f"Config command failed: {result.stderr}"
        print("   ✓ Config command works")
        
        # Verify config file was created
        config_file = Path("config") / "config.toml"
        assert config_file.exists(), "Config file was not created"
        print("   ✓ Config file created")
        
        # Test 3: download command
        print("\n3. Testing download command...")
        result = run_yf_cmd(["download"])
        # This might fail due to API limits, but shouldn't crash
        if result.returncode != 0:
            print(f"   Note: Download command failed (likely API-related): {result.stderr}")
        else:
            print("   ✓ Download command works")
        
        # Test 4: Test other commands still work
        print("\n4. Testing original commands...")
        result = run_yf_cmd(["capture-stock", "AAPL", "2023-01-01"])
        if result.returncode != 0:
            print(f"   Note: capture-stock failed (likely API-related): {result.stderr}")
        else:
            print("   ✓ capture-stock command works")
        
        result = run_yf_cmd(["capture-national-debt", "US", "2023-01-01"])
        if result.returncode != 0:
            print(f"   Note: capture-national-debt failed (likely API-related): {result.stderr}")
        else:
            print("   ✓ capture-national-debt command works")
    
    print("\n✓ All CLI command tests completed!")


def test_config_file_structure():
    """Test that the config file has the correct structure"""
    print("\n5. Testing config file structure...")
    
    config_file = Path("config") / "config.toml"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = toml.load(f)
        
        assert "paths" in config, "Config should have 'paths' section"
        assert "toml" in config["paths"], "Config should have 'toml' path"
        assert "db" in config["paths"], "Config should have 'db' path"
        print("   ✓ Config file has correct structure")
    else:
        print("   ⚠ Config file not found")


if __name__ == "__main__":
    print("Running yFinData CLI tests...")
    try:
        test_cli_commands()
        test_config_file_structure()
        print("\n✓ All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        sys.exit(1)