import functools
from datetime import date
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.finances import SheetSpending, Spending
from src.settings import SPREADSHEET_ID

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

TABLE_HEADERS = [SheetSpending.model_fields[el].description for el in SheetSpending.model_fields]


def get_credentials(
        service_account_file: str,
        scopes: list[str],
) -> service_account.Credentials:
    return service_account.Credentials.from_service_account_file(
        filename=service_account_file,
        scopes=scopes,
    )


def find_sub_sheet(sheet, name):
    for sheet in sheet.get("sheets", []):
        if sheet["properties"]["title"] == name:
            return sheet["properties"]["sheetId"]


def generate_sub_sheet_name(year, month):
    return f"{year}-{month}"


def create_sub_sheet(sheet_service, name):
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": name,
                    }
                }
            }
        ]
    }

    result = sheet_service.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
    return result


def check_sub_sheet_desigend(sheets_service, sub_sheet_name):
    request_data = sheets_service.values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=[f"{sub_sheet_name}!A1:C1"]
    ).execute()
    top_row_values = request_data["valueRanges"][0].get("values", [])
    if top_row_values:
        return True
    return False


def column_letter(column_index):
    letter = ''
    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter


def design_sub_sheet(sheets_service, sub_sheet_name, sub_sheet_id):
    fields = TABLE_HEADERS
    num_fields = len(fields)

    # Calculate the end column letter
    end_column_letter = column_letter(num_fields)

    # Request body for updating values
    values_body = {
        "valueInputOption": 'RAW',
        "data": [
            {
                "range": f"{sub_sheet_name}!A1:{end_column_letter}1",
                "majorDimension": 'ROWS',
                "values": [fields]
            }
        ],
        "includeValuesInResponse": False,
        "responseValueRenderOption": "UNFORMATTED_VALUE",
        "responseDateTimeRenderOption": "FORMATTED_STRING"
    }

    # Formatting requests
    format_requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sub_sheet_id,  # Replace with your actual sheet ID
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_fields
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.0,
                            "green": 0.0,
                            "blue": 0.0
                        },
                        "textFormat": {
                            "foregroundColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 1.0
                            },
                            "fontSize": 12,
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)"
            }
        },
        # Additional formatting requests can be added here
    ]

    # Execute value update
    sheets_service.values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=values_body).execute()

    # Execute formatting update
    sheets_service.batchUpdate(spreadsheetId=SPREADSHEET_ID, body={"requests": format_requests}).execute()

    return {"status": "Design and values updated successfully"}


def append_to_last_row(sheets_service, spreadsheet_id, sheet_name, sheet_id, data):
    # Calculate the range to search for the last row with data
    search_range = f"{sheet_name}!A1:A"

    # Get the last row with data
    result = sheets_service.values().get(spreadsheetId=spreadsheet_id, range=search_range).execute()
    values = result.get('values', [])

    # Determine the row number to start appending data
    # If 'values' is empty, start from row 1, otherwise, start from the next row after the last row with data
    start_row = len(values) + 1

    # Define the range to append data
    append_range = f"{sheet_name}!A{start_row}"

    # Append the data
    body = {'values': data}
    for index, value in enumerate(body['values']):
        for inner_index, inner_value in enumerate(value):
            if isinstance(inner_value, date):
                body['values'][index][inner_index] = inner_value.strftime("%Y-%m-%d")

    response = sheets_service.values().append(
        spreadsheetId=spreadsheet_id,
        range=append_range,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()

    # Get the range of the appended data for formatting reset
    updates = response.get('updates', {})
    updated_range = updates.get('updatedRange', '')
    start_row_index = updated_range.split('!')[-1].lstrip('A').split(':')[0]

    # Prepare the format reset request
    format_reset_request = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,  # Replace with the actual sheet ID
                        "startRowIndex": int(start_row_index) - 1,  # Convert to 0-based index
                        "endRowIndex": int(start_row_index) - 1 + len(data),
                    },
                    "cell": {
                        "userEnteredFormat": {}  # Specify the default format settings
                    },
                    "fields": "userEnteredFormat"  # Reset all format settings
                }
            }
        ]
    }

    # Send the format reset request
    sheets_service.batchUpdate(spreadsheetId=spreadsheet_id, body=format_reset_request).execute()


@functools.lru_cache()
def get_sheets_service():
    credentials = get_credentials(
        service_account_file="service_credentials.json",
        scopes=SCOPES,
    )

    return build("sheets", "v4", credentials=credentials).spreadsheets()


def read_spreedsheet(year, month, day=None):
    sheets_service = get_sheets_service()

    try:
        sheet = sheets_service.get(spreadsheetId=SPREADSHEET_ID).execute()
    except HttpError as e:
        raise ValueError(f"Error while reading spreadsheet: {e}")

    sub_sheet_name = generate_sub_sheet_name(year, month)

    sub_sheet_id = find_sub_sheet(sheet, sub_sheet_name)

    if sub_sheet_id is None:
        return []

    num_fields = len(TABLE_HEADERS)

    # Calculate the end column letter
    end_column_letter = column_letter(num_fields)

    return sheets_service.values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=[f"{sub_sheet_name}!A1:{end_column_letter}"]).execute()


def get_spendings(year, month, day=None) -> List[SheetSpending]:
    sheet_data = read_spreedsheet(year, month, day)
    if not sheet_data:
        return []
    sheet_data = sheet_data["valueRanges"][0].get("values", [])[1:]
    spendings = [SheetSpending.from_list(s) for s in sheet_data]
    if day:
        spendings = [s for s in spendings if s.datetime.day == day]
    return spendings


def add_spending(spending: Spending):
    sheets_spending = SheetSpending.from_spending(spending)

    sheets_service = get_sheets_service()

    sheet = sheets_service.get(spreadsheetId=SPREADSHEET_ID).execute()

    sub_sheet_name = generate_sub_sheet_name(spending.datetime.year, spending.datetime.month)

    sub_sheet_id = find_sub_sheet(sheet, sub_sheet_name)

    if sub_sheet_id is None:
        sub_sheet_id = create_sub_sheet(sheets_service, sub_sheet_name)
        sub_sheet_id = sub_sheet_id["replies"][0]["addSheet"]["properties"]["sheetId"]
        design_sub_sheet(sheets_service, sub_sheet_name, sub_sheet_id)

    append_to_last_row(
        sheets_service=sheets_service,
        spreadsheet_id=SPREADSHEET_ID,
        sheet_name=sub_sheet_name,
        sheet_id=sub_sheet_id,
        data=[list(sheets_spending.model_dump().values())]
    )

    return {"status": "Values updated successfully"}

# if __name__ == "__main__":
#     add_spending(sheets_service, sub_sheet_id, sub_sheet_name, SAMPLE_SPREADSHEET_ID, mock_spending)
