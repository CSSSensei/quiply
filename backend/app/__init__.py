from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    from app.routes import auth, quips, comments, users, health
    
    app.register_blueprint(health.bp, url_prefix="/api/v1")
    app.register_blueprint(auth.bp, url_prefix="/api/v1/auth")
    app.register_blueprint(quips.bp, url_prefix="/api/v1/quips")
    app.register_blueprint(comments.bp, url_prefix="/api/v1/quips")
    app.register_blueprint(users.bp, url_prefix="/api/v1/users")
    
    return app
