import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, app
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")


def create_database():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'), 
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS ordering (id_item INTEGER, item INTEGER, cost_usd REAL, delivery_time DATE)")
    conn.commit()
    cur.close()
    conn.close()

def get_credentials() -> Credentials:
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        filename='service_account.json', scopes=scopes
    )
    return credentials

def get_values():
    sheet_id = os.getenv("SHEET_ID")
    range_name = os.getenv("RANGE_NAME")
    credentials = get_credentials()
    service = build('sheets', 'v4', credentials=credentials)
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    return values

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'), 
        user=os.getenv('POSTGRES_USER'), 
        password=os.getenv('POSTGRES_PASSWORD'), 
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    cur = conn.cursor()
    values = get_values()

    for row in values:
        cur.execute("INSERT INTO ordering (id_item, item, cost_usd, delivery_time) VALUES (%s, %s, %s, %s);", (row[0], row[1], row[2], row[3]))
        conn.commit()

    cur.close()
    conn.close()

@app.route('/')
def index():
    create_database()
    get_db_connection()
    return 'it works'


if __name__ == "__main__":
    app.run()