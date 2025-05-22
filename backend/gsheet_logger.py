# --- Imports ---
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import os

# --- Config ---
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'absolute-keel-460616-g2-381e10284818.json'  # Replace with your actual path
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)

def create_sheet_for_csv(csv_filename):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    sheet_title = f"MergeLog_{os.path.splitext(csv_filename)[0]}_{timestamp}"

    # Create sheet
    spreadsheet = sheets_service.spreadsheets().create(
        body={
            'properties': {'title': sheet_title}
        },
        fields='spreadsheetId'
    ).execute()

    sheet_id = spreadsheet['spreadsheetId']

    # Set header row
    headers = [["Name", "City", "Audio URL", "Timestamp"]]
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Sheet1!A1:D1',
        valueInputOption='RAW',
        body={'values': headers}
    ).execute()

    # Optional: save to local file for use in future merge requests
    with open('active_sheet_id.txt', 'w') as f:
        f.write(sheet_id)

    return sheet_id

def append_row_to_active_sheet(name, city, audio_url):
    try:
        with open('active_sheet_id.txt', 'r') as f:
            sheet_id = f.read().strip()
    except FileNotFoundError:
        raise Exception("No active Google Sheet found. Create one with create_sheet_for_csv().")

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = [[name, city, audio_url, timestamp]]

    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range='Sheet1!A:D',
        valueInputOption='USER_ENTERED',
        body={'values': row}
    ).execute()

    return True
