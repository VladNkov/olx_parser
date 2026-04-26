import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

GOOGLE_CREDENTIALS = "/Users/apple/Documents/gitProjects/olx_parser/credentials/status-analitics-a9f75b3b3b5e.json"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME", "ads")


def write_ads_in_google_sheet(ads_data):
    gc = gspread.service_account(filename=GOOGLE_CREDENTIALS)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=30)

    headers = list(ads_data[0].keys())

    rows = [headers]

    for ad in ads_data:
        row = []

        for header in headers:
            row.append(ad.get(header, ''))

        rows.append(row)

    worksheet.clear()
    worksheet.update(values=rows, range_name='A1')

    print(f'Write {len(ads_data)} ads to Google Sheet')
    print(f'Added at: {datetime.now()}')


    # value = all_prices['sheet_1mm_1000_2000']
    # worksheet.update(range_name='E8:F8', values=[[value['name'], value['price']]])

