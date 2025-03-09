"""Tests for the GeoGuessr API client."""

from unittest.mock import MagicMock, patch

import pytest

from geoguessr_daily_tracker.api import GeoGuessrAPI


@pytest.fixture
def mock_api():
    """Create a mock API client with a fake cookie."""
    with patch.dict("os.environ", {"NCFA_COOKIE": "test_cookie"}):
        return GeoGuessrAPI()


def test_api_init_requires_cookie():
    """Test that API initialization requires a cookie."""
    with patch.dict("os.environ", clear=True):
        with pytest.raises(ValueError):
            GeoGuessrAPI()


def test_api_init_with_cookie():
    """Test that API initialization works with a cookie."""
    api = GeoGuessrAPI(cookie="test_cookie")
    assert api.ncfa_cookie == "test_cookie"
    assert api.headers == {"Cookie": "_ncfa=test_cookie"}


@patch("requests.get")
def test_get_daily_challenge(mock_get, mock_api):
    """Test getting the daily challenge token."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "authorCreator": {
            "id": "test_id",
            "name": "Test User",
            "avatarImage": "test_image",
            "signupAssetIds": [],
            "signupCoins": 0,
            "youtubeLink": "",
            "twitchLink": "",
            "twitterLink": "",
            "instagramLink": "",
        },
        "date": "2025-01-01T00:00:00Z",
        "participants": 1000,
        "token": "test_token",
        "pickedWinner": False,
        "leaderboard": [],
        "friends": [],
        "country": [],
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call the method
    token = mock_api.get_daily_challenge()

    # Assertions
    assert token == "test_token"
    mock_get.assert_called_once_with(
        "https://www.geoguessr.com/api/v3/challenges/daily-challenges/today",
        headers={"Cookie": "_ncfa=test_cookie"},
    )
