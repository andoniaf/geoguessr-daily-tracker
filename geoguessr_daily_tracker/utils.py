"""Utility functions for GeoGuessr Tracker."""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .config import get_data_dir
from .models import DailyChallengeGame


def save_to_csv(game: DailyChallengeGame, filename: Optional[Path] = None) -> None:
    """Save game results to CSV file.

    Args:
        game (DailyChallengeGame): The game results to save
        filename (Path, optional): Path to CSV file. If None, uses default location.
    """
    if filename is None:
        filename = get_data_dir() / "daily_challenges.csv"

    headers = [
        "date",
        "total_score",
        "total_distance",
        "round1_score",
        "round1_distance",
        "round2_score",
        "round2_distance",
        "round3_score",
        "round3_distance",
        "round4_score",
        "round4_distance",
        "round5_score",
        "round5_distance",
        "link",
    ]

    row_data = {
        "date": game.date.strftime("%Y-%m-%d"),
        "link": f"https://www.geoguessr.com/results/{game.token}",
        "total_score": game.totalScore,
        "total_distance": game.totalDistance,
    }

    for round in game.rounds:
        row_data[f"round{round.roundNumber}_score"] = round.score
        row_data[f"round{round.roundNumber}_distance"] = round.distance

    file_exists = os.path.isfile(filename)

    if file_exists:
        with open(filename, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["date"] == game.date.strftime("%Y-%m-%d"):
                    print(
                        f"Entry for {game.date.strftime('%Y-%m-%d')} already exists in the CSV file"
                    )
                    return

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row_data)
        print(f"Added new entry for {game.date.strftime('%Y-%m-%d')} to the CSV file")


def get_previous_challenges() -> Dict[datetime.date, str]:
    """Read previous challenge IDs from CSV file.

    Returns:
        Dict[datetime.date, str]: Mapping of dates to challenge IDs
    """
    challenges = {}
    csv_path = get_data_dir() / "previous_daily_links.csv"

    try:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = datetime.strptime(row["Date"], "%d/%m/%Y").date()
                challenge_id = row["URL"].split("/")[-1]
                challenges[date] = challenge_id
    except FileNotFoundError:
        print(f"Warning: {csv_path} not found")
        return {}

    return challenges
