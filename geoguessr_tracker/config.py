"""Configuration management for GeoGuessr Tracker."""

import json
import os
from pathlib import Path
from typing import Any, Dict

CONFIG_FILE = Path.home() / ".geoguessr_tracker.json"


def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables and config file.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    config = {}

    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass

    # Environment variables take precedence
    env_vars = {
        "NCFA_COOKIE": os.getenv("NCFA_COOKIE"),
        "USE_GSHEETS": os.getenv("USE_GSHEETS"),
        "GSHEET_ID": os.getenv("GSHEET_ID"),
        "GSHEET_CREDENTIALS": os.getenv("GSHEET_CREDENTIALS"),
    }

    # Update config with non-None environment variables
    config.update({k: v for k, v in env_vars.items() if v is not None})

    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file.

    Args:
        config (Dict[str, Any]): Configuration to save
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_data_dir() -> Path:
    """Get the data directory path.

    Returns:
        Path: Path to data directory
    """
    # Check if we're in development mode (package directory exists)
    repo_data_dir = Path(__file__).parent.parent / "data"
    if repo_data_dir.exists():
        return repo_data_dir

    # Otherwise use user data directory
    user_data_dir = Path.home() / ".geoguessr_tracker"
    user_data_dir.mkdir(exist_ok=True)
    return user_data_dir
