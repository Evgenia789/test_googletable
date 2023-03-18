import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """A class used to represent base config"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """A class used to represent production config"""
    FLASK_ENV = 'production'
    DEBUG = False


class DevelopmentConfig(Config):
    """A class used to represent development config"""
    FLASK_ENV = 'development'
    DEVELOPMENT = True
    DEBUG = True
