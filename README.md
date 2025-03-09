# GeoGuessr Daily Challenge Tracker

A Python package to track your GeoGuessr daily challenge scores and save them to CSV and Google Sheets.

## Features

- Fetches your daily challenge results from GeoGuessr
- Saves scores and distances for each round
- Stores results in a CSV file with links to each game
- Optional Google Sheets integration with formatting
- Command-line interface for easy tracking
- Prevents duplicate entries for the same day

## Requirements

- Python 3.10+
- GeoGuessr account cookie
- (Optional) Google Service Account credentials for Google Sheets integration

## Installation

### From PyPI

```bash
pip install geoguessr-daily-tracker
```

### From Source
```bash
git clone https://github.com/yourusername/geoguessr-daily-tracker.git
cd geoguessr-daily-tracker
pip install -e .
```

## Configuration

You can configure the tracker using environment variables or the configuration command:

```bash
# Interactive configuration
python -m geoguessr_daily_tracker.cli configure

# Show current configuration
python -m geoguessr_daily_tracker.cli configure --show
```

### Environment Variables
```bash
export NCFA_COOKIE="your_cookie_value_here"

# Optional: For Google Sheets integration
export USE_GSHEETS="true"
export GSHEET_ID="your_spreadsheet_id"
export GSHEET_CREDENTIALS="path/to/service-account.json"
```

## Usage
### Command Line
```python
# Track today's daily challenge
python -m geoguessr_daily_tracker.cli track

# Fill previous dates from CSV file
python -m geoguessr_daily_tracker.cli fill
```

### Python API
```python
from geoguessr_daily_tracker.api import GeoGuessrAPI
from geoguessr_daily_tracker.utils import save_to_csv

# Initialize API client
api = GeoGuessrAPI(cookie="your_cookie_value")

# Get today's challenge
token = api.get_daily_challenge()

# Get game details
game = api.get_game_details(token)

# Save to CSV
save_to_csv(game)
```

## Data Format

The CSV file contains the following columns:

    date: The date of the challenge
    total_score: Your total score for the game
    total_distance: Total distance in meters
    round[1-5]_score: Score for each round
    round[1-5]_distance: Distance in meters for each round
    link: Direct link to the game results

Google Sheets Setup (optional)

    Create a Google Cloud Project
    Enable Google Sheets API
    Create a Service Account with no roles
    Download the service account key
    Share your Google Sheet with the service account email (with Editor permissions)
    Copy the Spreadsheet ID from the URL

## Development
### Running Tests
```bash
pytest
```

## TODO
- [x] Add more formatting to the sheet
- [x] Add a feature to reingest past results
- [x] Add tests
    - [ ] Review AI generated tests 😅
- [ ] Add simple graph with results stats
- [ ] Automate getting previous_daily_links
