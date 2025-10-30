"""Tests for the CLI interface."""

import subprocess
import sys
from pathlib import Path


def test_cli_help():
    """Test that the CLI help works."""
    # Use the package entry point instead of direct module execution
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.cli", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Check that the new commands are present in help
    assert "add" in result.stdout
    assert "update" in result.stdout
    # Verify that the removed commands are not in help
    assert "capture-stock" not in result.stdout
    assert "capture-national-debt" not in result.stdout


def test_add_command():
    """Test that the add command exists."""
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.cli", "add", "AAPL", "2023-01-01"],
        capture_output=True,
        text=True
    )
    # The command might fail due to missing config, but shouldn't crash
    # Should have a proper error message, not an 'unknown command' error
    assert "No such command" not in result.stderr
    assert "add" in result.stdout or "Configuration file not found" in result.stderr


def test_update_command():
    """Test that the update command exists."""
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.cli", "update"],
        capture_output=True,
        text=True
    )
    # The command might fail due to missing config, but shouldn't crash
    # Should have a proper error message, not an 'unknown command' error
    assert "No such command" not in result.stderr
    assert "update" in result.stdout or "Configuration file not found" in result.stderr


def test_removed_commands():
    """Test that the removed commands are no longer available."""
    # Test that capture-stock command is no longer available
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.cli", "capture-stock", "AAPL", "2023-01-01"],
        capture_output=True,
        text=True
    )
    # Should return error about the command not existing
    assert result.returncode != 0
    assert "No such command 'capture-stock'" in result.stderr
    
    # Test that capture-national-debt command is no longer available
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.cli", "capture-national-debt", "US", "2023-01-01"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "No such command 'capture-national-debt'" in result.stderr
