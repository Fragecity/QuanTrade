"""
Shared constants for the yFinData project.
"""

# Treasury symbols mapping - used as proxy for national debt data
TREASURY_SYMBOLS = {
    "US": "^TNX",  # 10-year Treasury yield
    "USA": "^TNX",
    "United States": "^TNX",
}

# Default TOML configuration structure
DEFAULT_TOML_CONFIG = {
    'stocks': [
        {
            'name': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        }
    ],
    'national_debt': [
        {
            'name': 'US',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        }
    ]
}