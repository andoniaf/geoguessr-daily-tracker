# GeoGuessr Daily Challenge Tracker

A simple Python script to track your GeoGuessr daily challenge scores and save them to a CSV file.

## Features

- Fetches your daily challenge results from GeoGuessr
- Saves scores and distances for each round
- Stores results in a CSV file with links to each game
- Prevents duplicate entries for the same day

## Requirements

- Python 3.10+
- GeoGuessr account cookie

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Set your GeoGuessr cookie as an environment variable:
```bash
export NCFA_COOKIE="your_cookie_value_here"
```

2. Run the script:
```bash
python daily_challenge_tracker.py
```

The script will create a CSV file named `daily_challenges.csv` in the current directory with your game results.

## CSV Format

The CSV file contains the following columns:
- date: The date of the challenge
- total_score: Your total score for the game
- total_distance: Total distance in meters
- round[1-5]_score: Score for each round
- round[1-5]_distance: Distance in meters for each round
- link: Direct link to the game results

