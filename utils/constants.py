from dataclasses import dataclass


@dataclass
class Constants:
    """
    A dataclass representing the constants.
    """
    scopes = (
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            )
    credentials_file_path = 'service_account.json'
