from typing import List, Optional

import psycopg2

from app.database.googlesheet import GoogleSheetsManager
from utils.constants import Constants
from utils.currency_rate import get_currency_rate
from utils.telegram_message import send_message


class PostgresDB:
    """
    Singleton class that handles database connections and initialization.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new PostgresDB instance if one does not already exist,
        otherwise return the existing instance.
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self, dbname: Optional[str] = None,
                 user: Optional[str] = None, password: Optional[str] = None,
                 host: Optional[str] = None, port: Optional[int] = None):
        """
        Initialize the PostgresDB instance with the provided credentials.

        :param dbname: The name of the database to connect to.
        :param user: The username to use for the database connection.
        :param password: The password to use for the database connection.
        :param host: The hostname or IP address of the server running
                     the database.
        :param port: The port number to use for the database connection.
        """
        if self.__initialized:
            return
        self.__initialized = True
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None
        self.currency_rate = None

    def connect(self) -> None:
        """
        Connect to the PostgreSQL database using the provided credentials.

        :return: None
        :raises: If there is an error connecting to the database.
        """
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
        except psycopg2.Error as error:
            print(f"Error connecting to PostgreSQL database: {error}")
            raise

    def create_database(self) -> None:
        """
        Creates a new table in the connected PostgreSQL database
        if it doesn't exist already.

        :return: None
        :raise: If there is an error creating the table.
        """
        if not self.cursor:
            self.connect()
        try:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS "
                "ordering (id_item INTEGER, item INTEGER, cost_usd REAL, delivery_time DATE, cost_rub REAL)")
            self.connection.commit()
        except psycopg2.Error as e:
            print(f"Error creating database: {e}")
            raise

    def execute(self, query: str, params: Optional[tuple] = None) -> None:
        """
        Executes the provided SQL query using the current database connection.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters to include with the query.
        :return: None
        :raise: If there is an error executing the query.
        """
        if not self.cursor:
            self.connect()
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except psycopg2.Error as error:
            print(f"Error executing query: {error}")
            self.connection.rollback()
            raise

    def disconnect(self) -> None:
        """
        Closes the current database connection and cursor if they are open.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def copy_data_from_googletable(self, values: List[List[str]]) -> None:
        """
        Copies the data from the specified Google Sheet to the PostgreSQL
        database.

        :param values: A list of rows from the Google Sheet, where each row
                       is a list of strings representing the values in each
                       column.
        :return: None
        :raise: If there is an error executing the database query.
        """
        self.currency_rate = get_currency_rate()
        try:
            for row in values:
                self.cursor.execute(
                    "INSERT INTO ordering (id_item, item, cost_usd, delivery_time, cost_rub) "
                    f"VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{str(int(float(row[2]) * self.currency_rate))}');"
                )
                self.connection.commit()
        except psycopg2.Error as error:
            print(f"Error copy data: {error}")
            raise

    def change_data(self) -> None:
        """
        Retrieves data from a Google Sheet using the GoogleSheetsManager,
        deletes all existing data from the table in the database, and
        inserts the new data into the 'ordering' table.

        :return: None
        :raise: If an error occurs while deleting or inserting data into
                 the database.
        """
        manager = GoogleSheetsManager(
            credentials_file_path=Constants.credentials_file_path
        )
        if manager.check_changes():
            try:
                values = manager.get_values()
                self.cursor.execute("DELETE FROM ordering;")
                self.copy_data_from_googletable(values)
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")
                raise

    def update_currency_rate(self) -> None:
        """
        Update the currency rate in the database and update the cost_rub for
        all rows if necessary.

        :return: None
        :raise: If an error occurs while updating the data in the database.
        """
        current_rate = get_currency_rate()
        try:
            if current_rate != self.currency_rate:
                self.cursor.execute(
                    f"UPDATE ordering SET cost_rub=cost_usd*'{current_rate}';"
                )
                self.connection.commit()
            return
        except psycopg2.Error as e:
            print(f"Error updating data: {e}")
            raise

    def get_all_data(self):
        """
        Retrieves all data from the 'ordering' table.

        :return: A list of tuples representing the data from the table.
        """
        try:
            self.cursor.execute("SELECT * FROM ordering;")
            self.connection.commit()
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error getting data: {e}")
            raise

    def check_dates(self):
        """
        Checks the ordering database for any orders that have a delivery_time
        earlier than the current date, and sends a message with the
        corresponding item names if any are found.

        :raise: If there is an error executing the database query.
        """
        try:
            self.cursor.execute(
                "SELECT item FROM ordering WHERE delivery_time < CURRENT_DATE;"
            )
            self.connection.commit()
            results = self.cursor.fetchall()
            orders = [str(order[0]) for order in results]
            if orders:
                send_message(", ".join(orders))
        except psycopg2.Error as e:
            print(f"Error getting data: {e}")
            raise
