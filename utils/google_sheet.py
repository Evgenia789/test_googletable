import os

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from typing import List

from utils.currency_rate import get_currency_rate
from utils.constants import Constants


def get_credentials() -> Credentials:
    """
    Returns Google API credentials required to access a Google Sheets API.
    This function reads the service account file 'service_account.json' in the
    specified directory, and returns a `Credentials` object with the necessary
    authorization information to access the Google Sheets API.

    :return: A `Credentials` object with authorization information.
    """
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        filename='service_account.json', scopes=scopes
    )
    return credentials


def get_rub_rate() -> None:
    """
    Updates the ruble rate column in a Google Sheet
    with the latest conversion rates.

    :return: None
    :raises Exception: If any errors occur during the execution of the
                       function, such as the `get_currency_rate()`
                       function failing or if the Google Sheet cannot
                       be accessed.
    """
    try:
        current_rate = get_currency_rate()
        sheet_id = os.getenv("SHEET_ID")
        credentials = get_credentials()
        client = gspread.authorize(credentials=credentials)
        sheet = client.open_by_url(
            f'https://docs.google.com/spreadsheets/d/{sheet_id}'
        )
        worksheet = sheet.get_worksheet(0)
        col_values = worksheet.col_values(Constants.column_number_from)[1:]
        new_values = [
            int(float(col_values[i]) * current_rate)
            for i in range(len(col_values))
        ]
        data_for_insert = [Constants.column_name] + new_values
        worksheet.insert_cols(values=[data_for_insert],
                              col=Constants.column_number_to)
        return
    except Exception as e:
        print(f"An error occurred: {e}")


def get_values() -> List[List[str]]:
    """
    Retrieves values from a Google Sheet.

    :return: A list of lists containing the values in the specified range
             of the Google Sheet.
    :rtype: List[List[str]]
    :raises Exception: If any errors occur during the execution of the
                       function, such as the `get_rub_rate()` function
                       failing or if the Google Sheet cannot be accessed.
    """
    try:
        get_rub_rate()
        sheet_id = os.getenv("SHEET_ID")
        range_name = os.getenv("RANGE_NAME")
        credentials = get_credentials()
        service = build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=range_name
        ).execute()
        values = result.get('values', [])

        return values
    except Exception as e:
        print(f"An error occurred: {e}")
