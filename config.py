from os import environ, path

basedir = path.abspath(path.dirname(__file__))


class Config:
    """Set Flask configuration vars"""

    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_ENV = environ.get('FLASK_ENV')
    FLASK_DEBUG = environ.get('FLASK_DEBUG', False)
    TESTING = environ.get('FLASK_DEBUG', False)

    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

