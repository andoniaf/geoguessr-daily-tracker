"""Tests for the Google Sheets integration."""

from unittest.mock import MagicMock, patch

import pytest

from geoguessr_tracker.sheets import GoogleSheetsWriter


@pytest.fixture
def mock_sheets_env():
    """Set up environment variables for sheets testing."""
    with patch.dict(
        "os.environ",
        {
            "GSHEET_ID": "test_sheet_id",
            "GSHEET_CREDENTIALS": "test_credentials.json",
        },
    ):
        yield


@pytest.fixture
def mock_credentials():
    """Mock the credentials file loading."""
    with patch(
        "google.oauth2.service_account.Credentials.from_service_account_file"
    ) as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_sheets_service():
    """Mock the Google Sheets service."""
    with patch("googleapiclient.discovery.build") as mock:
        service_mock = MagicMock()
        mock.return_value = service_mock
        yield service_mock


def test_sheets_init_requires_config(mock_credentials, mock_sheets_service):
    """Test that sheets initialization requires configuration."""
    with patch.dict("os.environ", clear=True):
        with pytest.raises(ValueError):
            GoogleSheetsWriter()


def test_sheets_init_with_config(
    mock_sheets_env, mock_credentials, mock_sheets_service
):
    """Test that sheets initialization works with configuration."""
    writer = GoogleSheetsWriter()
    assert writer.spreadsheet_id == "test_sheet_id"
    mock_credentials.assert_called_once()
