import json
from os import path
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

config_data = {}
if path.exists("config.json"):
    with open("config.json") as file:
        config_data = json.load(file)
db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()
admin_username = ""
admin_password = ""

limiter_string = config_data.get("rate_limiting_string", "60 per minute")
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[limiter_string])


def db_init_app(app):
    """
    The function to initialize Flask Object for SQLAlchemy object.

    Parameters:
        app (Flask): The Flask Object that SQLAlchemy object needs.

    Returns:
        SQLAlchemy: SQLAlchemy object that interacts with database.       
    """
    db.app = app
    db.init_app(app)
    return db


def db_create_tables(app):
    """
    The function to create table in database.

    Parameters:
        app (Flask): The Flask Object that SQLAlchemy object needs.

    Returns:
        MockConnection: MockConnection object that connects to database.       
    """
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    db.create_all()
    db.session.commit()
    return engine


def ma_init_app(app):
    """
    The function to initialize Flask Object for Marshmallow object.

    Parameters:
        app (Flask): The Flask Object that Marshmallow object needs.

    Returns:
        Marshmallow: Marshmallow object that handles query output.      
    """
    ma.app = app
    ma.init_app(app)
    return ma


def bcrypt_init_app(app):
    """
    The function to initialize Flask Object for Bcrypt object.

    Parameters:
        app (Flask): the Flask Object that Bcrypt object needs.

    Returns:
        Bcrypt: Bcrypt object that handles hashing, verifying hashes and plain text.      
    """
    bcrypt.app = app
    bcrypt.init_app(app)
    return bcrypt


def limiter_init_app(app):
    """
    The function to initialize Flask Object for Limiter object.

    Parameters:
        app (Flask): the Flask Object that Limiter object needs.

    Returns:
        limiter: Limiter object that Rate Limiting Rules.      
    """
    limiter.app = app
    limiter.init_app(app)
    return limiter
