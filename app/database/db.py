import psycopg2

from utils.google_sheet import get_values


class PostgresDB:

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        print("__init__")
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        print("connect")
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            raise

    def create_database(self):
        print("create database")
        if not self.cursor:
            self.connect()
        try:
            print("start create database")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS ordering (id_item INTEGER, item INTEGER, cost_usd REAL, delivery_time DATE, cost_rub REAL)")
            self.connection.commit()
            print("finish create database")
            print("start copy googletable")
            self.copy_data_from_googletable()
            print("finish copy googletable")
        except psycopg2.Error as e:
            print(f"Error creating database: {e}")
            raise

    def execute(self, query, params=None):
        if not self.cursor:
            self.connect()
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            raise

    def fetchall(self):
        if not self.cursor:
            print("make connect fot fetchall")
            self.connect()
        try:
            print("return cursor for fetchall")
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching results: {e}")
            raise

    def disconnect(self):
        print("disconnect")
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def copy_data_from_googletable(self):
        print("start processing copy")
        values = get_values()
        try:
            for row in values:
                self.cursor.execute("INSERT INTO ordering (id_item, item, cost_usd, delivery_time, cost_rub) VALUES (%s, %s, %s, %s, %s);", (row[0], row[1], row[2], row[3], row[4]))
                self.connection.commit()
            print("finish processing copy")
        except psycopg2.Error as e:
            print(f"Error copy data: {e}")
            raise
