import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
load_dotenv()

#local file
#GOOGLE_SHEETS_CREDENTIALS_FILE = "./southern-flash-479404-v0-e17ef4cbcd38.json"
#SPREADSHEET_ID = "1X-ZDU-DWwKbk3OoVqzdDV6BIJqtTwHBCTVKED_FipUE"

#read json
#GOOGLE_SHEETS_CREDENTIALS_JSON =os.getenv("service_acc_secret_file")
SPREADSHEET_ID = os.getenv("g_sheet_id")
#print(json.loads(os.getenv("service_acc_secret_file")))
GOOGLE_SHEETS_CREDENTIALS_JSON = json.loads(os.getenv("service_acc_secret_file"))


# json_str = os.getenv("service_acc_secret_file")
# GOOGLE_SHEETS_CREDENTIALS_JSON = json.loads(json_str)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
HEADERS = [
    "Timestamp",
    "From",
    "Subject",
    "Category",
    "Summary",
    "Body",
    "email_link"
]

# function to resize rows for the whole sheet
def set_default_row_height(worksheet, height=30):
    """
    Sets the default row height for the entire sheet.
    Applies formatting using Google Sheets API batchUpdate.
    """
    gc = get_gspread_client()
    sh = gc.open_by_key(SPREADSHEET_ID)

    sheet_id = worksheet._properties['sheetId']

    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": 0,     # apply from row 1 (0-based)
                        "endIndex": 1000     # or a very large number
                    },
                    "properties": {
                        "pixelSize": height
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }

    sh.batch_update(body)

def ensure_headers(worksheet):
    try:
        existing = worksheet.row_values(1)
    except:
        existing = []

   # hearders correction
    if not existing or existing != HEADERS:
        worksheet.resize(1)  # clear first row
        worksheet.update("A1:F1", [HEADERS])

# def build_gmail_link(message_id):
#     if not message_id:
#         return ""
#     message_id_clean = message_id.strip("<>")
#     return f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{message_id_clean}"

def get_gspread_client():
    # READS FILE
    # creds = Credentials.from_service_account_file(
    #     GOOGLE_SHEETS_CREDENTIALS_FILE,
    #     scopes=SCOPES
    # )

    # # READS JSON
    creds = Credentials.from_service_account_info(
        GOOGLE_SHEETS_CREDENTIALS_JSON,
        scopes=SCOPES
    )
    print("sheet credentials are good")
    return gspread.authorize(creds)

def append_email_row(category, email_dict, summary):
    gc = get_gspread_client()
    sheetid = gc.open_by_key(SPREADSHEET_ID)


    ws_name = {
        "Sales": "Sales",
        "Support": "Support",
        "Feedback": "Feedback",
        "Other": "Other"
    }.get(category, "Other")

    try:
        ws = sheetid.worksheet(ws_name)
    except gspread.WorksheetNotFound:
        ws = sheetid.add_worksheet(title=ws_name, rows=1000, cols=10)

    ensure_headers(ws)

    import datetime
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    # email_link = build_gmail_link(email_dict["message_id"])

    row = [
        timestamp,
        email_dict["from"],
        email_dict["subject"],
        category,
        summary,
        email_dict["body"][:5000],
        # email_link
    ]
    ws.append_row(row, value_input_option="USER_ENTERED")




