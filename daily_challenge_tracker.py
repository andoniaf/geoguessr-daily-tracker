import os
import csv
from datetime import datetime
import requests
from models import DailyChallengeResponse, GameResponse, DailyChallengeGame, Round

class GeoGuessrAPI:
    BASE_URL = "https://www.geoguessr.com/api/v3"
    
    def __init__(self):
        self.ncfa_cookie = os.getenv("NCFA_COOKIE")
        if not self.ncfa_cookie:
            raise ValueError("NCFA_COOKIE environment variable is required")
        
        self.headers = {
            "Cookie": f"_ncfa={self.ncfa_cookie}"
        }
    
    def get_daily_challenge(self) -> str:
        response = requests.get(
            f"{self.BASE_URL}/challenges/daily-challenges/today",
            headers=self.headers
        )
        response.raise_for_status()
        challenge_data = DailyChallengeResponse(**response.json())
        return challenge_data.token
    
    def get_game_details(self, token: str) -> DailyChallengeGame:
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
            date=datetime.now()
        )

def save_to_csv(game: DailyChallengeGame, filename: str = "daily_challenges.csv"):
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

def main():
    try:
        api = GeoGuessrAPI()
        token = api.get_daily_challenge()
        game = api.get_game_details(token)
        save_to_csv(game)
        print(f"Successfully saved daily challenge results for {game.date}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 