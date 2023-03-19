import os
from typing import Any, List, Optional

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.constants import Constants


class GoogleSheetsManager:
    """
    Singleton class that handles Google Sheets connections and initialization.
    """
    __instance = None

    def __new__(cls, credentials_file_path: str):
        """
        Create a new GoogleSheetsManager instance if one does not already
        exist, otherwise return the existing instance.
        Initializes a GoogleSheetsManager instance.

        :param credentials_file_path: The path to the service account
                                      json file.
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            credentials = Credentials.from_service_account_file(
                credentials_file_path, scopes=Constants.scopes
            )
            client = gspread.authorize(credentials=credentials)
            sheet = client.open_by_url(
                url=f'https://docs.google.com/spreadsheets/d/{os.getenv("SHEET_ID")}'
            )
            cls.__instance.credentials = credentials
            cls.__instance.client = client
            cls.__instance.sheet = sheet
            cls.__instance.drive_service = build('drive', 'v3',
                                                 credentials=credentials)
            cls.__instance.sheets_service = build('sheets', 'v4',
                                                  credentials=credentials)
            cls.__instance.start_page_token = cls.__instance.fetch_start_page_token()
            cls.__instance.page_token = cls.__instance.fetch_start_page_token()

        return cls.__instance

    def fetch_start_page_token(self) -> Optional[str]:
        """
        Fetches the start page token from the Drive API.

        :return: The start page token as a string, or None
                 if it cannot be fetched.
        :raises Exception: If there is an error fetching the start page token.
        """
        try:
            response = self.drive_service.changes().getStartPageToken().execute()
        except HttpError as error:
            print(F'An error occurred: {error}')
            response = None

        return response.get('startPageToken')

    def get_values(self) -> List[List[Any]]:
        """
        Gets the values of the sheet from the first row to the last row.

        :return: A list of lists representing the cell values of the sheet,
                 where each inner list represents a row.
        :raises: RuntimeError: If the API request fails for any reason.
        """
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=os.getenv("SHEET_ID"),
            range=f'orders!A2:D{self.get_last_row()}'
        ).execute()
        values = result.get('values', [])

        return values

    def check_changes(self) -> bool:
        """
        Checks if there have been any changes to the Google Sheet since
        the last time the function was called.

        :return: A boolean value indicating whether there were changes
                 (True) or not (False).
        :raises: If there is an error while checking for changes.
        """
        self.page_token = self.start_page_token
        were_changes_in_a_file = False

        try:
            while self.page_token is not None:
                response = self.drive_service.changes().list(
                    pageToken=self.page_token,
                    spaces='drive',
                ).execute()
                for change in response.get('changes'):
                    were_changes_in_a_file = True
                    print(F'Change found for file: {change.get("fileId")}')
                if 'newStartPageToken' in response:
                    self.start_page_token = response.get('newStartPageToken')
                self.page_token = response.get('nextPageToken')

        except Exception as error:
            print(F'An error occurred: {error}')
        finally:
            return were_changes_in_a_file

    def get_last_row(self) -> int:
        """
        Returns the index of the last row in the first sheet of the workbook.

        :return: The index of the last row.
        :raises: ValueError: If the sheet is empty.
        """
        worksheet = self.sheet.get_worksheet(0)
        values = worksheet.get_values()
        num_rows = len(values)

        if num_rows == 0:
            raise ValueError("Sheet is empty.")

        return num_rows
