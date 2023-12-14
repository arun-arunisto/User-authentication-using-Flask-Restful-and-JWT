from flask import Flask
from src_app.authentication.views import authentication_bp
import os
from src_app.authentication.models import db
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(authentication_bp)
    return app
