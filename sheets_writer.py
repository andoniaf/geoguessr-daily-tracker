from typing import Dict, List
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from models import DailyChallengeGame

class GoogleSheetsWriter:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        self.spreadsheet_id = os.getenv('GSHEET_ID')
        credentials_path = os.getenv('GSHEET_CREDENTIALS')
        
        if not self.spreadsheet_id or not credentials_path:
            raise ValueError("GSHEET_ID and GSHEET_CREDENTIALS environment variables are required")
            
        self.credentials = Credentials.from_service_account_file(
            credentials_path, 
            scopes=self.SCOPES
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.GOLD_THRESHOLD = 22500
        self.SILVER_THRESHOLD = 20000
    
    def _get_existing_dates(self) -> List[str]:
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range='A2:A'
        ).execute()
        
        if 'values' not in result:
            return []
            
        return [row[0] for row in result.get('values', [])]
    
    def _get_sheet_values(self, range_name):
        """Get values from the sheet"""
        return self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
    
    def ensure_headers(self):
        """Ensure headers are present in the first row"""
        headers = [
            "Date", "Total Score", "Total Distance",
            "Round 1 Score", "Round 1 Distance",
            "Round 2 Score", "Round 2 Distance",
            "Round 3 Score", "Round 3 Distance",
            "Round 4 Score", "Round 4 Distance",
            "Round 5 Score", "Round 5 Distance",
            "Link"
        ]
        
        # Calculate the correct range based on number of headers
        last_column = chr(ord('A') + len(headers) - 1)  # Convert number to letter (A=0, B=1, etc)
        range_name = f'A1:{last_column}1'
        
        # Get current values in first row
        result = self._get_sheet_values(range_name)
        first_row = result.get('values', [[]])[0] if 'values' in result else []
        
        # If sheet is empty or headers don't match, add them
        if not first_row or first_row != headers:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={
                    'values': [headers]
                }
            ).execute()
    
    def apply_score_formatting(self):
        """Apply conditional formatting for score column"""
        requests = [
            # Clear existing conditional format rules first
            {
                "deleteConditionalFormatRule": {
                    "sheetId": 0,
                    "index": 0
                }
            },
            # Gold rule (≥ 22500)
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": 0,  # Assuming first sheet
                            "startColumnIndex": 1,  # Column B (Total Score)
                            "endColumnIndex": 2
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "NUMBER_GREATER_THAN_EQ",
                                "values": [{"userEnteredValue": str(self.GOLD_THRESHOLD)}]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 0.85,
                                    "blue": 0.0,
                                    "alpha": 1.0
                                }
                            }
                        }
                    }
                }
            },
            # Silver rule (between 20000 and 22499)
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": 0,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "NUMBER_BETWEEN",
                                "values": [
                                    {"userEnteredValue": str(self.SILVER_THRESHOLD)},
                                    {"userEnteredValue": str(self.GOLD_THRESHOLD - 1)}
                                ]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 0.8,
                                    "green": 0.8,
                                    "blue": 0.8,
                                    "alpha": 1.0
                                }
                            }
                        }
                    }
                }
            }
        ]

        try:
            # Try to delete existing rules first
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={"requests": [requests[0]]}
            ).execute()
        except:
            # If no rules exist, that's fine
            pass

        # Add new rules
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"requests": requests[1:]}
        ).execute()

    def save_game(self, game: DailyChallengeGame):
        self.ensure_headers()
        
        row_data = [
            game.date.strftime("%Y-%m-%d"),
            game.totalScore,
            game.totalDistance
        ]
        
        for round in game.rounds:
            row_data.extend([round.score, round.distance])
            
        row_data.append(f"https://www.geoguessr.com/results/{game.token}")
        
        existing_dates = self._get_existing_dates()
        if game.date.strftime("%Y-%m-%d") in existing_dates:
            print(f"Entry for {game.date.strftime('%Y-%m-%d')} already exists in the spreadsheet")
            return
            
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range='A1',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={
                'values': [row_data]
            }
        ).execute()
        
        # Apply conditional formatting after saving
        self.apply_score_formatting()
        
        print(f"Added new entry for {game.date.strftime('%Y-%m-%d')} to the spreadsheet") 