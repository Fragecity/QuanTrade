"""Tests for the installed CLI interface."""

import subprocess
import sys
from pathlib import Path


def test_installed_cli_help():
    """Test that the installed CLI help works."""
    # Test the installed CLI command using uv run
    result = subprocess.run(["uv", "run", "yFinData", "--help"], 
                            capture_output=True, text=True,
                            cwd=Path(__file__).parent.parent.parent)
    assert result.returncode == 0
    # Check that the new commands are present in help
    assert "add" in result.stdout
    assert "update" in result.stdout
    # Verify that the removed commands are not in help
    assert "capture-stock" not in result.stdout
    assert "capture-national-debt" not in result.stdout


def test_installed_add_command():
    """Test the installed add command."""
    # Test that the command exists and doesn't crash with basic arguments
    result = subprocess.run(["uv", "run", "yFinData", "add", "AAPL", "2023-01-01"], 
                            capture_output=True, text=True,
                            cwd=Path(__file__).parent.parent.parent)
    # Should have a proper error message about missing config, not 'unknown command'
    assert "No such command" not in result.stderr
    assert "Configuration file not found" in result.stderr


def test_installed_update_command():
    """Test the installed update command."""
    # Test that the command exists and doesn't crash with basic arguments
    result = subprocess.run(["uv", "run", "yFinData", "update"], 
                            capture_output=True, text=True,
                            cwd=Path(__file__).parent.parent.parent)
    # Should have a proper error message about missing config, not 'unknown command'
    assert "No such command" not in result.stderr
    assert "Configuration file not found" in result.stderr


def test_installed_removed_commands():
    """Test that the removed commands are no longer available in the installed CLI."""
    # Test that capture-stock command is no longer available
    result = subprocess.run(["uv", "run", "yFinData", "capture-stock", "AAPL", "2023-01-01"], 
                            capture_output=True, text=True,
                            cwd=Path(__file__).parent.parent.parent)
    # Should return error about the command not existing
    assert result.returncode != 0
    assert "No such command 'capture-stock'" in result.stderr
    
    # Test that capture-national-debt command is no longer available
    result = subprocess.run(["uv", "run", "yFinData", "capture-national-debt", "US", "2023-01-01"], 
                            capture_output=True, text=True,
                            cwd=Path(__file__).parent.parent.parent)
    # Should return error about the command not existing
    assert result.returncode != 0
    assert "No such command 'capture-national-debt'" in result.stderr