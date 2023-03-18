import os

from dotenv import load_dotenv
from flask import Flask, app

from app.database.db import PostgresDB

load_dotenv()


def get_flask_app(config: str = "config.ProductionConfig") -> app.Flask:
    """
    Initializes Flask app with given configuration.
    :param config: Configuration string
    :return: app
    """
    app = Flask(__name__)
    app.config.from_object(config)

    database = PostgresDB(dbname=os.getenv('POSTGRES_DB'),
                          user=os.getenv('POSTGRES_USER'),
                          password=os.getenv('POSTGRES_PASSWORD'),
                          host=os.getenv('DB_HOST'),
                          port=os.getenv('DB_PORT'))
    database.create_database()

    @app.route('/')
    def index():
        database.execute("SELECT * FROM ordering")
        results = database.fetchall()
        return f'it works /n {results}'

    return app


if __name__ == "__main__":
    app = get_flask_app()
    app.run()
