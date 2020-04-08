from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

db = SQLAlchemy()

Base = declarative_base()

Base.query = db.session.query_property()


def create_app(config=None):
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    if config:
        app.config.update(config)

    from application import models
    db.init_app(app)

    with app.app_context():
        from . import routes

        if not database_exists(db.engine.url):
            create_database(db.engine.url)
        Base.metadata.create_all(bind=db.engine)

        return app
