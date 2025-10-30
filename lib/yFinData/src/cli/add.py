import click
from datetime import datetime
from pathlib import Path
import sys
import toml as toml_lib
from get_stock.stock_struct import capture_stock
from database.database import capture_data


def get_config_path():
    """Get the path to the configuration file."""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.toml"


@click.command(name='add')
@click.argument('stock', type=str)
@click.argument('start_date', type=str)
def add_command(stock: str, start_date: str):
    """
    Add a new stock to the TOML configuration or update an existing one.
    
    STOCK is the stock ticker symbol (e.g., 'AAPL').
    START_DATE is the start date in YYYY-MM-DD format.
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
    
    # Validate the date format
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        click.echo(f"Invalid date format: {start_date}. Please use YYYY-MM-DD format.", err=True)
        sys.exit(1)
    
    # Set end date to today by default
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Load the TOML configuration
    with open(toml_path, 'r') as f:
        toml_config = toml_lib.load(f)
    
    # Ensure stocks section exists
    if 'stocks' not in toml_config:
        toml_config['stocks'] = []
    
    # Check if the stock already exists in the configuration
    stock_exists = False
    for stock_entry in toml_config['stocks']:
        if stock_entry['name'].upper() == stock.upper():
            # Update the existing stock entry
            stock_entry['start_date'] = start_date
            stock_entry['end_date'] = end_date
            stock_exists = True
            click.echo(f"Updated existing stock: {stock} with start date {start_date}")
            break
    
    # If stock doesn't exist, add it to the configuration
    if not stock_exists:
        toml_config['stocks'].append({
            'name': stock.upper(),
            'start_date': start_date,
            'end_date': end_date
        })
        click.echo(f"Added new stock: {stock} with start date {start_date}")
    
    # Save the updated TOML configuration
    with open(toml_path, 'w') as f:
        toml_lib.dump(toml_config, f)
    
    # Now capture the data for the stock
    try:
        click.echo(f"Capturing data for {stock} from {start_date} to {end_date}...")
        # This will capture the data based on the updated TOML file
        capture_data(db_path, toml_path)
        click.echo(f"Successfully added/updated {stock} and captured data.")
    except Exception as e:
        click.echo(f"Error capturing data for {stock}: {e}", err=True)
        sys.exit(1)