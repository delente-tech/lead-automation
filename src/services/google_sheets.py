import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config import settings

def get_sheet_client():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.CREDENTIALS_FILE, scope
    )
    client = gspread.authorize(creds)
    return client.open_by_key(settings.GOOGLE_SHEET_ID).worksheet(settings.SHEET_NAME)
