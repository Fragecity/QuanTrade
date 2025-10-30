# yFinData

A CLI tool for managing stock and national debt data with yfinance.

## Overview

yFinData is a command-line interface tool that helps you capture, manage, and update financial data including stock prices and national debt information (proxied by treasury yields). The tool uses yfinance to retrieve data and stores it in an SQLite database according to a configurable TOML file.

## Features

- Initialize data directories with database and configuration files
- Add new stocks to your configuration or update existing ones
- Update existing data to the latest available, downloading only missing data
- Download data based on your configuration
- Configure TOML and database file paths

## Installation

This package is part of the QuanTrade project and is managed using uv. To install:
```bash
uv pip install -e lib/yFinData
```

## Usage

### Available Commands

- `yFinData add <stock> <start_date>` - Add a new stock to the TOML configuration or update an existing one
- `yFinData config` - Configure TOML and database file paths
- `yFinData download` - Download data based on configured TOML file and store in configured database
- `yFinData init <directory>` - Initialize a data directory with stock.db and stock.toml files
- `yFinData update` - Update existing data to the latest available, downloading only missing data

### Getting Started

1. **Initialize a data directory**:
   ```bash
   yFinData init data
   ```

2. **Configure file paths**:
   ```bash
   yFinData config --toml data/stock.toml --db data/stock.db
   ```

3. **Add a stock to your configuration**:
   ```bash
   yFinData add AAPL 2023-01-01
   ```

4. **Update data to the latest**:
   ```bash
   yFinData update
   ```

### Configuration

The tool uses a TOML configuration file to specify which stocks and national debt data to track. Here's an example structure:

```toml
[[stocks]]
name = "AAPL"
start_date = "2023-01-01"
end_date = "2023-12-31"

[[national_debt]]
name = "DGS10"
start_date = "2023-01-01"
end_date = "2023-12-31"
```

## Architecture

The yFinData library is organized into the following modules:

- `cli/` - Command-line interface implementations
- `database/` - Database creation and data capture functions
- `get_stock/` - Core functionality for capturing stock and national debt data
- `utils.py` - Shared data processing functions
- `constants.py` - Treasury symbols mapping and default TOML configuration

## Command Details

### `add <stock> <start_date>`
- Adds a new stock to the configuration or updates an existing one
- Automatically captures data for the specified stock
- The end date defaults to today

### `config`
- Sets up paths to the TOML configuration file and database
- Creates a config file to remember these paths

### `download`
- Downloads data based on the configured TOML file
- Stores the data in the configured database

### `init <directory>`
- Creates a new data directory
- Sets up an SQLite database file and a TOML configuration file

### `update`
- Updates existing data to the latest available
- Only downloads missing data, making it efficient
- Works with both stocks and national debt data

## Development

### Running Tests

To run the test suite:

```bash
cd lib/yFinData
uv run python -m pytest
```

### Project Structure

- `src/` - Source code for the library
- `tests/` - Test suite
- `data/` - Default location for data files (created with `init` command)

## Dependencies

- yfinance: For retrieving financial data
- click: For building the command-line interface
- toml: For processing configuration files
- sqlite3: For database operations (built into Python)

## License

See the main project license.