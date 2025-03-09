"""Command-line interface for GeoGuessr Tracker."""

import argparse
import sys
from typing import Optional

from .api import GeoGuessrAPI
from .config import get_config
from .sheets import GoogleSheetsWriter
from .utils import get_previous_challenges, save_to_csv


def setup_sheets() -> Optional[GoogleSheetsWriter]:
    """Initialize and return Google Sheets writer if enabled.

    Returns:
        GoogleSheetsWriter or None: Sheets writer instance if enabled
    """
    config = get_config()
    if config.get("USE_GSHEETS", "").lower() == "true":
        try:
            return GoogleSheetsWriter()
        except Exception as e:
            print(f"Warning: Failed to initialize Google Sheets: {e}")
    return None


def fill_daily_challenge(api: GeoGuessrAPI, sheets_writer, date, challenge_id):
    """Fill challenge data for a specific date and challenge ID.

    Args:
        api (GeoGuessrAPI): API client instance
        sheets_writer: GoogleSheetsWriter instance or None
        date (datetime.date): The date of the challenge
        challenge_id (str): The challenge ID from the URL
    """
    try:
        game = api.get_game_details(challenge_id)
        game.date = date
        save_to_csv(game)
        if sheets_writer:
            sheets_writer.save_game(game)
        print(f"Successfully saved challenge results for {date}")
    except Exception as e:
        print(f"Error filling challenge for {date}: {str(e)}")


def fill_previous_dates(api: GeoGuessrAPI, sheet):
    """Fill previous dates using challenge IDs from CSV.

    Args:
        api (GeoGuessrAPI): API client instance
        sheet: GoogleSheetsWriter instance or None
    """
    challenges = get_previous_challenges()
    for date, challenge_id in challenges.items():
        print(f"Filling data for {date} with challenge {challenge_id}")
        fill_daily_challenge(api, sheet, date, challenge_id)


def configure_command(args):
    """Handle the configure command.

    Args:
        args: Command-line arguments
    """
    config = get_config()

    if args.show:
        # Hide sensitive values when showing config
        display_config = config.copy()
        if "NCFA_COOKIE" in display_config:
            display_config["NCFA_COOKIE"] = (
                "****" + display_config["NCFA_COOKIE"][-4:]
                if display_config["NCFA_COOKIE"]
                else None
            )
        print("Current configuration:")
        for key, value in display_config.items():
            print(f"  {key}: {value}")
        return

    # Interactive configuration
    print("GeoGuessr Tracker Configuration")
    print("==============================")
    print("Press Enter to keep current value")

    cookie = input(
        f"GeoGuessr _ncfa cookie [{config.get('NCFA_COOKIE', '****') if config.get('NCFA_COOKIE') else 'not set'}]: "
    )
    if cookie:
        config["NCFA_COOKIE"] = cookie

    use_sheets = input(
        f"Use Google Sheets? (true/false) [{config.get('USE_GSHEETS', 'false')}]: "
    )
    if use_sheets:
        config["USE_GSHEETS"] = use_sheets.lower()

    if config.get("USE_GSHEETS", "").lower() == "true":
        sheet_id = input(f"Google Sheet ID [{config.get('GSHEET_ID', 'not set')}]: ")
        if sheet_id:
            config["GSHEET_ID"] = sheet_id

        creds_path = input(
            f"Path to Google service account credentials [{config.get('GSHEET_CREDENTIALS', 'not set')}]: "
        )
        if creds_path:
            config["GSHEET_CREDENTIALS"] = creds_path

    from .config import save_config

    save_config(config)
    print("Configuration saved successfully")


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(description="GeoGuessr Daily Challenge Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Track command
    subparsers.add_parser("track", help="Track today's daily challenge")

    # Fill command
    subparsers.add_parser("fill", help="Fill previous dates from CSV file")

    # Configure command
    config_parser = subparsers.add_parser("configure", help="Configure the application")
    config_parser.add_argument(
        "--show", action="store_true", help="Show current configuration"
    )

    args = parser.parse_args()

    if args.command == "configure":
        configure_command(args)
        return

    try:
        api = GeoGuessrAPI()
        sheet = setup_sheets()

        if args.command == "fill":
            fill_previous_dates(api, sheet)
        elif args.command == "track" or args.command is None:
            # Default command is track
            token = api.get_daily_challenge()
            game = api.get_game_details(token)
            save_to_csv(game)
            if sheet:
                sheet.save_game(game)
            print(f"Successfully saved challenge results for {game.date}")
        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
