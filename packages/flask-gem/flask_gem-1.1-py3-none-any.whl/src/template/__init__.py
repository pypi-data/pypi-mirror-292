"""Application root."""
import os

from flask import Flask
from flask_migrate import Migrate

from .database import db

migrate = Migrate()

def create_app(config_mode):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///{}/app.db'.format(os.getcwd())
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    return app
