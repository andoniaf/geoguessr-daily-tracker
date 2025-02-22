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
    
    def format_sheet(self):
        """Apply all sheet formatting including headers, colors, column widths and number formats"""
        headers = [
            "Date", "Total Score",
            "Round 1 Score", "Round 1 Distance",
            "Round 2 Score", "Round 2 Distance",
            "Round 3 Score", "Round 3 Distance",
            "Round 4 Score", "Round 4 Distance",
            "Round 5 Score", "Round 5 Distance",
            "Total Distance", "Link"
        ]
        
        requests = []
        
        # Clear all existing formatting first
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(headers)
                },
                "fields": "userEnteredFormat"
            }
        })

        # Get current values in first row
        result = self._get_sheet_values('A1:N1')
        first_row = result.get('values', [[]])[0] if 'values' in result else []
        
        # Only update headers if they're missing or different
        if not first_row or first_row != headers:
            requests.append({
                "updateCells": {
                    "rows": [{
                        "values": [{
                            "userEnteredValue": {"stringValue": header},
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.1,
                                    "green": 0.27,
                                    "blue": 0.13
                                },
                                "textFormat": {
                                    "bold": True,
                                    "foregroundColor": {
                                        "red": 1.0,
                                        "green": 1.0,
                                        "blue": 1.0
                                    }
                                }
                            }
                        } for header in headers]
                    }],
                    "fields": "userEnteredValue,userEnteredFormat",
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(headers)
                    }
                }
            })
        else:
            # If headers exist but need formatting
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": len(headers)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.1,
                                "green": 0.27,
                                "blue": 0.13
                            },
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {
                                    "red": 1.0,
                                    "green": 1.0,
                                    "blue": 1.0
                                }
                            }
                        }
                    },
                    "fields": "userEnteredFormat"
                }
            })

        # Alternating column colors
        for i in range(0, len(headers), 2):
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 1,  # Skip header
                        "startColumnIndex": i,
                        "endColumnIndex": i + 2 if i + 2 <= len(headers) else len(headers)
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.95 if i % 4 == 0 else 0.9,
                                "green": 0.98 if i % 4 == 0 else 0.95,
                                "blue": 0.95 if i % 4 == 0 else 0.9
                            }
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

        # Default column widths
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": len(headers)
                },
                "properties": {
                    "pixelSize": 100
                },
                "fields": "pixelSize"
            }
        })

        # Hide distance columns
        distance_columns = [3, 5, 7, 9, 11]  # Columns D, F, H, J, L (round distances)
        for col_index in distance_columns:
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": 0,
                        "dimension": "COLUMNS",
                        "startIndex": col_index,
                        "endIndex": col_index + 1
                    },
                    "properties": {
                        "pixelSize": 0,
                        "hiddenByUser": True
                    },
                    "fields": "pixelSize,hiddenByUser"
                }
            })

        # Score formatting
        score_columns = [
            (1, 2),   # Total Score
            (2, 3),   # Round 1 Score
            (4, 5),   # Round 2 Score
            (6, 7),   # Round 3 Score
            (8, 9),   # Round 4 Score
            (10, 11)  # Round 5 Score
        ]

        for start_col, end_col in score_columns:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": 1,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "NUMBER",
                                "pattern": "#,##0"
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            })

        # Score conditional formatting (gold/silver)
        requests.extend([
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": 0,
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
        ])

        # Apply all formatting
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"requests": requests}
        ).execute()

    def save_game(self, game: DailyChallengeGame):
        # Apply formatting first
        self.format_sheet()

        """Save game results to the spreadsheet"""
        row_data = [
            game.date.strftime("%Y-%m-%d"),
            game.totalScore
        ]
        
        for round in game.rounds:
            row_data.extend([round.score, round.distance])
            
        # Add total distance just before the link
        row_data.extend([
            game.totalDistance,
            f"https://www.geoguessr.com/results/{game.token}"
        ])
        
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
        
        print(f"Added new entry for {game.date.strftime('%Y-%m-%d')} to the spreadsheet") 