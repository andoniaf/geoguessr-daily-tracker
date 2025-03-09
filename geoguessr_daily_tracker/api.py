"""API client for GeoGuessr game interactions."""

from datetime import datetime

import requests

from .config import get_config
from .models import DailyChallengeGame, DailyChallengeResponse, GameResponse, Round


class GeoGuessrAPI:
    """API client for GeoGuessr game interactions."""

    BASE_URL = "https://www.geoguessr.com/api/v3"

    def __init__(self, cookie=None):
        """Initialize the API client with required authentication.

        Args:
            cookie (str, optional): The _ncfa cookie value. If not provided,
                                   will be read from environment or config.
        """
        self.ncfa_cookie = cookie or get_config().get("NCFA_COOKIE")
        if not self.ncfa_cookie:
            raise ValueError("NCFA_COOKIE is required in environment or config")

        self.headers = {"Cookie": f"_ncfa={self.ncfa_cookie}"}

    def get_daily_challenge(self) -> str:
        """Fetch today's daily challenge token.

        Returns:
            str: The challenge token

        Raises:
            requests.RequestException: If API request fails
        """
        response = requests.get(
            f"{self.BASE_URL}/challenges/daily-challenges/today", headers=self.headers
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
            f"{self.BASE_URL}/challenges/{token}/game", headers=self.headers
        )
        response.raise_for_status()
        game_data = GameResponse(**response.json())

        rounds = [
            Round(
                score=guess.roundScoreInPoints,
                distance=guess.distanceInMeters,
                roundNumber=i + 1,
            )
            for i, guess in enumerate(game_data.player.guesses)
        ]

        return DailyChallengeGame(
            token=token,
            totalScore=int(game_data.player.totalScore.amount),
            totalDistance=game_data.player.totalDistanceInMeters,
            rounds=rounds,
            date=datetime.now().date(),
        )
