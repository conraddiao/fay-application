import os
import requests
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("CSE_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_JSON")

def google_search(query, num_results=10):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'num': min(num_results, 10)
    }

    results = []
    start = 1
    while len(results) < num_results:
        params['start'] = start
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' not in data:
            print("No more results or error:", data)
            break

        for item in data['items']:
            results.append([item.get('title'), item.get('link'), item.get('snippet')])
        
        start += 10
        if len(data['items']) < 10:
            break

    return results

def write_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    sheet.clear()
    sheet.append_row(["Title", "Link", "Snippet"])
    for row in data:
        sheet.append_row(row)
    print(f"Wrote {len(data)} rows to Google Sheet.")

# === MAIN ===
if __name__ == "__main__":
    query = 'intext:"faynutrition.com/dietitians/"'
    results = google_search(query, num_results=200)
    write_to_gsheet(results)
