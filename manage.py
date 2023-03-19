import os
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, current_app, jsonify

from app.database.db import PostgresDB
from app.database.googlesheet import GoogleSheetsManager
from utils.constants import Constants

load_dotenv()


def index() -> List:
    """
    Get all data from the ordering table in the database and return as
    a JSON response.

    :return: A list of tuples representing the data in the ordering table.
    """
    with current_app.app_context():
        values = current_app.config['database'].get_all_data()
    return jsonify(values)


def create_app(config: str = "config.ProductionConfig") -> Flask:
    """
    Create a Flask application instance with the specified
    configuration settings.

    :param config: The name of the configuration class to use.
                   Defaults to "config.ProductionConfig".

    :return: The Flask application instance.
    """
    app_instance = Flask(__name__)
    app_instance.config.from_object(config)
    manager = GoogleSheetsManager(
        credentials_file_path=Constants.credentials_file_path
    )
    database = PostgresDB(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    database.create_database()
    database.copy_data_from_googletable(values=manager.get_values())

    app_instance.config['manager'] = manager
    app_instance.config['database'] = database

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=database.change_data,
        trigger='interval',
        minutes=5
    )
    scheduler.add_job(
        func=database.update_currency_rate,
        trigger='interval',
        hours=12,
    )
    scheduler.add_job(
        func=database.check_dates,
        trigger='interval',
        minutes=1
        # hours=12,
    )
    scheduler.start()

    app_instance.add_url_rule('/', 'index', index)
    return app_instance


if __name__ == "__main__":
    app_instance = create_app()
    app_instance.run()
