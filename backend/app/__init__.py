from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_cors import CORS

from config import config
from app.utils.errors import BaseAPIError
from app.utils.response import APIResponse
from app.utils.logger import setup_logger, log_error

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
logger = setup_logger()


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    @app.before_request
    def before_request():
        try:
            if hasattr(get_jwt_identity(), '__call__'):
                user_id = get_jwt_identity()
                if user_id:
                    g.user_id = int(user_id)
        except Exception:
            pass
    
    @app.errorhandler(BaseAPIError)
    def handle_api_error(error):
        log_error(logger, error)
        return APIResponse.error(
            message=error.message,
            status_code=error.status_code,
            error_code=error.error_code,
            details=error.details
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return APIResponse.error(
            message="Resource not found",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        log_error(logger, error, {"original_error": str(error)})
        return APIResponse.error(
            message="Internal server error",
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR"
        )
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        log_error(logger, error, {"unexpected": True})
        return APIResponse.error(
            message="An unexpected error occurred",
            status_code=500,
            error_code="UNEXPECTED_ERROR"
        )
    
    from app.routes import auth, quips, comments, users, health
    
    app.register_blueprint(health.bp, url_prefix="/api/v1")
    app.register_blueprint(auth.bp, url_prefix="/api/v1/auth")
    app.register_blueprint(quips.bp, url_prefix="/api/v1/quips")
    app.register_blueprint(comments.bp, url_prefix="/api/v1/quips")
    app.register_blueprint(users.bp, url_prefix="/api/v1/users")
    
    return app
