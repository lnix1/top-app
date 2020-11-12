from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/top_app"
    app.config['SECRET_KEY'] = 'dev'
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app

top_app = create_app()
#heroku = Heroku(top_app)
db = SQLAlchemy(top_app)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), unique=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def __repr__(self):
        return '<User %r>' % (self.username)

def register_blueprint(app):
    from top_app import views
    app.register_blueprint(views.bp)
    return app

top_app = register_blueprint(top_app)