import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/top_app'
    db = SQLAlchemy(app)

    return db
