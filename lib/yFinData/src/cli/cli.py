import click
from datetime import datetime
import sys
from math import isnan
import os
from pathlib import Path
import toml as toml_lib
from get_stock.stock_struct import capture_stock, capture_national_debt
from database.database import create_database, capture_data
from .update import update_command
from .add import add_command


@click.group()
def cli():
    """CLI tool for managing stock and national debt data with yfinance."""
    pass


# Add the update command to the CLI group
cli.add_command(update_command)

# Add the add command to the CLI group
cli.add_command(add_command)


def get_config_path():
    """Get the path to the configuration file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.toml"


@cli.command(name='config')
@click.option('--toml', type=click.Path(exists=True), help='Path to the TOML configuration file')
@click.option('--db', type=click.Path(exists=True), help='Path to the database file')
def config_command(toml: str, db: str):
    """
    Configure TOML and database file paths.
    """
    config_path = get_config_path()
    
    # Load existing config if it exists
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = toml_lib.load(f)
    else:
        config = {}
    
    # Ensure paths section exists
    if "paths" not in config:
        config["paths"] = {}
    
    # Update the configuration
    if toml:
        config["paths"]["toml"] = toml
        click.echo(f"Configured TOML file: {toml}")
    
    if db:
        config["paths"]["db"] = db
        click.echo(f"Configured database file: {db}")
    
    # Save the configuration
    with open(config_path, 'w') as f:
        toml_lib.dump(config, f)
    
    click.echo(f"Configuration saved to: {config_path}")


@cli.command(name='download')
def download_command():
    """
    Download data based on configured TOML file and store in configured database.
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        click.echo("Configuration file not found. Please run 'yFinData config' first.", err=True)
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = toml_lib.load(f)
    
    paths = config.get("paths", {})
    toml_path = paths.get("toml")
    db_path = paths.get("db")
    
    if not toml_path:
        click.echo("TOML file path not configured. Please run 'yFinData config --toml' first.", err=True)
        sys.exit(1)
    
    if not db_path:
        click.echo("Database file path not configured. Please run 'yFinData config --db' first.", err=True)
        sys.exit(1)
    
    try:
        # Capture data from TOML to database
        capture_data(db_path, toml_path)
        click.echo(f"Downloaded data from {toml_path} to {db_path}")
    except Exception as e:
        click.echo(f"Error downloading data: {e}", err=True)
        sys.exit(1)


@cli.command(name='init')
@click.argument('directory', type=str)
def init_command(directory: str):
    """
    Initialize a data directory with stock.db and stock.toml files.
    
    DIRECTORY is the directory to initialize (e.g., 'data').
    """
    try:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        
        db_file = dir_path / "stock.db"
        toml_file = dir_path / "stock.toml"
        
        # Create the database and TOML files
        create_database(str(db_file), str(toml_file))
        
        click.echo(f"Initialized data directory: {directory}")
        click.echo(f"  - Created database: {db_file}")
        click.echo(f"  - Created config: {toml_file}")
        
    except Exception as e:
        click.echo(f"Error initializing data directory: {e}", err=True)
        sys.exit(1)








def main():
    cli()


if __name__ == "__main__":
    main()
