import click
from pathlib import Path
import sys
import toml as toml_lib
from get_stock.update import update_missing_data


def get_config_path():
    """Get the path to the configuration file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.toml"


@click.command(name='update')
def update_command():
    """
    Update existing data to the latest available, downloading only missing data.
    
    This command reads from the configured TOML file and updates the database
    by only downloading data that is missing from the database. It does not
    re-download existing data, making it more efficient than a full re-download.
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
        # Update missing data in the database based on the TOML configuration
        click.echo(f"Updating data in {db_path} using configuration from {toml_path}")
        update_missing_data(db_path, toml_path)
        click.echo("Data update completed successfully.")
    except Exception as e:
        click.echo(f"Error updating data: {e}", err=True)
        sys.exit(1)