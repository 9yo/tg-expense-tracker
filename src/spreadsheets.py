"""Module for handling spreadsheet operations."""

import functools
import logging
from datetime import date
from typing import Any, Dict, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.finances import SheetSpending, Spending
from src.settings import SERVICE_ACCOUNT_FILE_PATH, SPREADSHEET_ID

logger = logging.getLogger(__name__)
# Constants
SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
)
TABLE_HEADERS = tuple(
    SheetSpending.model_fields[el].description for el in SheetSpending.model_fields
)


def get_credentials(service_account_file: str) -> service_account.Credentials:
    """Obtain credentials from a service account file."""
    return service_account.Credentials.from_service_account_file(
        filename=service_account_file,
        scopes=SCOPES,
    )


def find_sub_sheet(sheet_data: Dict[str, Any], name: str) -> Optional[int]:
    """Find a sub-sheet by name within a sheet."""
    for sheet_properties in sheet_data.get("sheets", []):
        if sheet_properties["properties"]["title"] == name:
            return sheet_properties["properties"]["sheetId"]
    return None


def generate_sub_sheet_name(year: int, month: int) -> str:
    """Generate a name for a sub-sheet based on year and month."""
    return f"{year}-{month}"


def create_sub_sheet(sheet_service: Any, name: str) -> Dict[str, Any]:
    """Create a new sub-sheet with a specified name."""
    body = {"requests": [{"addSheet": {"properties": {"title": name}}}]}
    return sheet_service.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()


def check_sub_sheet_designed(sheets_service: Any, sub_sheet_name: str) -> bool:
    """Check if a sub-sheet has a specific design."""
    request_data = (
        sheets_service.values()
        .batchGet(
            spreadsheetId=SPREADSHEET_ID,
            ranges=[f"{sub_sheet_name}!A1:C1"],
        )
        .execute()
    )
    return bool(request_data["valueRanges"][0].get("values", []))


def column_letter(column_index: int) -> str:
    """Convert a column index to a letter."""
    letter = ""
    while column_index > 0:
        column_index, remainder = divmod(column_index - 1, 26)  # noqa: WPS432
        letter = chr(65 + remainder) + letter  # noqa: WPS432
    return letter


def design_sub_sheet(
    sheets_service: Any,
    sub_sheet_name: str,
    sub_sheet_id: int,
) -> Dict[str, str]:
    """Apply a specific design to a sub-sheet."""
    fields = TABLE_HEADERS
    num_fields = len(fields)
    end_column_letter = column_letter(num_fields)
    values_body = {
        "valueInputOption": "RAW",
        "data": [
            {
                "range": f"{sub_sheet_name}!A1:{end_column_letter}1",
                "majorDimension": "ROWS",
                "values": [fields],
            },
        ],
    }
    format_requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sub_sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": num_fields,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0, "green": 0, "blue": 0},
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "fontSize": 12,
                            "bold": True,
                        },
                    },
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            },
        },
    ]
    sheets_service.values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=values_body,
    ).execute()
    sheets_service.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": format_requests},
    ).execute()
    return {"status": "Design and values updated successfully"}


def append_to_last_row(  # noqa: WPS210
    sheets_service: Any,
    spreadsheet_id: str,
    sheet_name: str,
    sheet_id: int,
    row_data: List[List[Any]],
) -> None:
    # Calculate the range to search for the last row with data
    search_range = f"{sheet_name}!A1:A"

    # Get the last row with data
    sheets_values_request = (
        sheets_service.values()
        .get(spreadsheetId=spreadsheet_id, range=search_range)
        .execute()
    )

    # Determine the row number to start appending data
    # If 'values' is empty, start from row 1, otherwise, start after last row
    start_row = len(sheets_values_request.get("values", [])) + 1

    # Define the range to append data
    append_range = f"{sheet_name}!A{start_row}"

    # Append the data
    body = {"values": row_data}
    for index, value in enumerate(body["values"]):  # noqa: WPS110
        for inner_index, inner_value in enumerate(value):
            if isinstance(inner_value, date):
                body["values"][index][inner_index] = inner_value.strftime("%Y-%m-%d")

    response = (
        sheets_service.values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=append_range,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )

    # Get the range of the appended data for formatting reset
    updates = response.get("updates", {})
    updated_range = updates.get("updatedRange", "")
    start_row_index = (
        updated_range.split("!")[-1].lstrip("A").split(":")[0]  # noqa: WPS221
    )

    # Prepare the format reset request
    format_reset_request = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,  # Replace with the actual sheet ID
                        "startRowIndex": int(start_row_index)
                        - 1,  # Convert to 0-based index
                        "endRowIndex": int(start_row_index) - 1 + len(row_data),
                    },
                    "cell": {
                        "userEnteredFormat": {},  # Specify the default format settings
                    },
                    "fields": "userEnteredFormat",  # Reset all format settings
                },
            },
        ],
    }

    # Send the format reset request
    sheets_service.batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=format_reset_request,
    ).execute()


@functools.lru_cache()
def get_sheets_service() -> Any:
    credentials = get_credentials(
        service_account_file=SERVICE_ACCOUNT_FILE_PATH,
    )

    return build("sheets", "v4", credentials=credentials).spreadsheets()


def read_spreedsheet(year: int, month: int, day: Optional[int] = None) -> Any:
    sheets_service = get_sheets_service()

    try:
        sheet = sheets_service.get(spreadsheetId=SPREADSHEET_ID).execute()
    except HttpError as err:
        raise ValueError(f"Error while reading spreadsheet: {err}")

    sub_sheet_name = generate_sub_sheet_name(year, month)

    sub_sheet_id = find_sub_sheet(sheet, sub_sheet_name)

    if sub_sheet_id is None:
        return []

    # Calculate the end column letter
    end_column_letter = column_letter(len(TABLE_HEADERS))

    return (
        sheets_service.values()
        .batchGet(
            spreadsheetId=SPREADSHEET_ID,
            ranges=[f"{sub_sheet_name}!A1:{end_column_letter}"],
        )
        .execute()
    )


def get_spendings(
    year: int,
    month: int,
    day: Optional[int] = None,
) -> List[SheetSpending]:
    """
    Returns a list of SheetSpending objects.

    :param year: Specify the year of the spendings
    :param month: Specify which month to get the spendings from
    :param day: Filter the spendings by day
    :return: A list of sheetspending objects
    """
    sheet_data = read_spreedsheet(year, month, day)
    if not sheet_data:
        return []
    sheet_data = sheet_data["valueRanges"][0].get("values", [])[1:]
    spendings: List[SheetSpending] = [
        SheetSpending.from_list(shd) for shd in sheet_data
    ]
    if day:
        spendings = [spending for spending in spendings if spending.datetime.day == day]
    return spendings


def add_spending(spending_list: List[Spending]) -> Dict[str, str]:  # noqa: WPS210
    """
    Adds Spending it to the Google Sheets document.

    :param spending_list: List[Spending]: Specify the type of data that is expected to
        be passed into the function
    :return: A dictionary with a status key
    :returns: Dict[str, str]: A dictionary with a status key
    """

    spending_list: List[SheetSpending] = [
        SheetSpending.from_spending(spending) for spending in spending_list
    ]

    sheets_service = get_sheets_service()

    sheet = sheets_service.get(spreadsheetId=SPREADSHEET_ID).execute()

    spending_by_date: Dict[str, List[SheetSpending]] = {}

    for spending in spending_list:
        sub_sheet_name = generate_sub_sheet_name(
            spending.datetime.year,
            spending.datetime.month,
        )
        if sub_sheet_name not in spending_by_date:
            spending_by_date[sub_sheet_name] = []
        spending_by_date[sub_sheet_name].append(spending)

    for sub_sheet_name, spendings in spending_by_date.items():
        sub_sheet_id: Optional[int] = find_sub_sheet(sheet, sub_sheet_name)

        if sub_sheet_id is None:
            sub_sheet_response: Dict[str, Any] = create_sub_sheet(
                sheets_service,
                sub_sheet_name,
            )["replies"][0]["addSheet"]
            sub_sheet_id = sub_sheet_response["properties"]["sheetId"]
            design_sub_sheet(sheets_service, sub_sheet_name, sub_sheet_id)

        logger.info(f"Adding spending {spendings}")

        append_to_last_row(
            sheets_service=sheets_service,
            spreadsheet_id=SPREADSHEET_ID,
            sheet_name=sub_sheet_name,
            sheet_id=sub_sheet_id,
            row_data=[list(spending.model_dump().values()) for spending in spendings],
        )
    return {"status": "Values updated successfully"}
