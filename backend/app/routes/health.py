from flask import Blueprint, jsonify
from datetime import datetime
from app import db

bp = Blueprint("health", __name__)


@bp.route("/", methods=["GET"])
def api_info():
    return jsonify({
        "name": "Quiply API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "auth": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "me": "GET /api/v1/auth/me"
            },
            "quips": {
                "list": "GET /api/v1/quips",
                "create": "POST /api/v1/quips",
                "get": "GET /api/v1/quips/<id>",
                "upvote": "POST /api/v1/quips/<id>/up",
                "remove_upvote": "DELETE /api/v1/quips/<id>/up",
                "repost": "POST /api/v1/quips/<id>/repost"
            },
            "comments": {
                "list": "GET /api/v1/quips/<id>/comments",
                "create": "POST /api/v1/quips/<id>/comments",
                "upvote": "POST /api/v1/quips/comments/<id>/up",
                "remove_upvote": "DELETE /api/v1/quips/comments/<id>/up"
            },
            "users": {
                "profile": "GET /api/v1/users/<username>",
                "quips": "GET /api/v1/users/<username>/quips",
                "reposts": "GET /api/v1/users/<username>/reposts"
            }
        },
        "documentation": "https://github.com/CSSSensei/quiply"
    }), 200


@bp.route("/health", methods=["GET"])
def health_check():
    try:
        db.session.execute(db.text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return jsonify({
        "status": "ok" if db_status == "healthy" else "error",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }), 200 if db_status == "healthy" else 503
