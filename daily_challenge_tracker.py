import os
import csv
from datetime import datetime, timedelta
import requests
import argparse
from models import DailyChallengeResponse, GameResponse, DailyChallengeGame, Round
from sheets_writer import GoogleSheetsWriter

class GeoGuessrAPI:
    """API client for GeoGuessr game interactions."""
    
    BASE_URL = "https://www.geoguessr.com/api/v3"
    
    def __init__(self):
        """Initialize the API client with required authentication."""
        self.ncfa_cookie = os.getenv("NCFA_COOKIE")
        if not self.ncfa_cookie:
            raise ValueError("NCFA_COOKIE environment variable is required")
        
        self.headers = {
            "Cookie": f"_ncfa={self.ncfa_cookie}"
        }
    
    def get_daily_challenge(self) -> str:
        """Fetch today's daily challenge token.
        
        Returns:
            str: The challenge token
        
        Raises:
            requests.RequestException: If API request fails
        """
        response = requests.get(
            f"{self.BASE_URL}/challenges/daily-challenges/today",
            headers=self.headers
        )
        response.raise_for_status()
        challenge_data = DailyChallengeResponse(**response.json())
        return challenge_data.token
    
    def get_game_details(self, token: str) -> DailyChallengeGame:
        """Fetch game details for a specific challenge token.
        
        Args:
            token (str): The challenge token/ID

        Returns:
            DailyChallengeGame: Game details including score and rounds
            
        Raises:
            requests.RequestException: If API request fails
        """
        response = requests.get(
            f"{self.BASE_URL}/challenges/{token}/game",
            headers=self.headers
        )
        response.raise_for_status()
        game_data = GameResponse(**response.json())
        
        rounds = [
            Round(
                score=guess.roundScoreInPoints,
                distance=guess.distanceInMeters,
                roundNumber=i + 1
            )
            for i, guess in enumerate(game_data.player.guesses)
        ]
        
        return DailyChallengeGame(
            token=token,
            totalScore=int(game_data.player.totalScore.amount),
            totalDistance=game_data.player.totalDistanceInMeters,
            rounds=rounds,
            date=datetime.now().date()
        )

def save_game_results(game: DailyChallengeGame, sheets_writer=None):
    """Save game results to CSV and optionally to Google Sheets.
    
    Args:
        game (DailyChallengeGame): The game results to save
        sheets_writer (GoogleSheetsWriter, optional): Google Sheets writer instance
    """
    save_to_csv(game)
    
    if sheets_writer:
        sheets_writer.save_game(game)
        
    print(f"Successfully saved challenge results for {game.date}")

def save_to_csv(game: DailyChallengeGame, filename: str = "daily_challenges.csv"):
    """Save game results to CSV file.
    
    Args:
        game (DailyChallengeGame): The game results to save
        filename (str, optional): Path to CSV file. Defaults to "daily_challenges.csv"
    """
    headers = [
        "date", "total_score", "total_distance",
        "round1_score", "round1_distance",
        "round2_score", "round2_distance",
        "round3_score", "round3_distance",
        "round4_score", "round4_distance",
        "round5_score", "round5_distance",
        "link",
    ]
    
    row_data = {
        "date": game.date.strftime("%Y-%m-%d"),
        "link": f"https://www.geoguessr.com/results/{game.token}",
        "total_score": game.totalScore,
        "total_distance": game.totalDistance
    }
    
    for round in game.rounds:
        row_data[f"round{round.roundNumber}_score"] = round.score
        row_data[f"round{round.roundNumber}_distance"] = round.distance
    
    file_exists = os.path.isfile(filename)
    
    if file_exists:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['date'] == game.date.strftime("%Y-%m-%d"):
                    print(f"Entry for {game.date.strftime('%Y-%m-%d')} already exists in the CSV file")
                    return
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row_data)
        print(f"Added new entry for {game.date.strftime('%Y-%m-%d')} to the CSV file")

def get_previous_challenges():
    """Read previous challenge IDs from CSV file.
    
    Returns:
        dict: Mapping of dates to challenge IDs
    """
    challenges = {}
    try:
        with open('previous_daily_links.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = datetime.strptime(row['Date'], '%d/%m/%Y').date()
                challenge_id = row['URL'].split('/')[-1]
                challenges[date] = challenge_id
    except FileNotFoundError:
        print("Warning: previous_daily_links.csv not found")
        return {}
    return challenges

def setup_sheets():
    """Initialize and return Google Sheets writer if enabled.
    
    Returns:
        GoogleSheetsWriter or None: Sheets writer instance if enabled
    """
    if os.getenv('USE_GSHEETS', '').lower() == 'true':
        return GoogleSheetsWriter()
    return None

def fill_daily_challenge(sheets_writer, date, challenge_id):
    """Fill challenge data for a specific date and challenge ID.
    
    Args:
        sheets_writer: GoogleSheetsWriter instance or None
        date (datetime.date): The date of the challenge
        challenge_id (str): The challenge ID from the URL
    """
    try:
        api = GeoGuessrAPI()
        game = api.get_game_details(challenge_id)
        game.date = date
        save_game_results(game, sheets_writer)
    except Exception as e:
        print(f"Error filling challenge for {date}: {str(e)}")

def fill_previous_dates(sheet):
    """Fill previous dates using challenge IDs from CSV.
    
    Args:
        sheet: GoogleSheetsWriter instance or None
    """
    challenges = get_previous_challenges()
    for date, challenge_id in challenges.items():
        print(f"Filling data for {date} with challenge {challenge_id}")
        fill_daily_challenge(sheet, date, challenge_id)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--fill-previous', action='store_true', 
                        help='Fill previous dates from CSV file')
    args = parser.parse_args()

    sheet = setup_sheets()
    
    if args.fill_previous:
        fill_previous_dates(sheet)
        return

    try:
        api = GeoGuessrAPI()
        token = api.get_daily_challenge()
        game = api.get_game_details(token)
        save_game_results(game, sheet)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 