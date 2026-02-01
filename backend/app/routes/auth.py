from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        user = AuthService.register(username, email, password)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        token = AuthService.login(username, password)
        return jsonify({"token": token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "created_at": user.created_at.isoformat()
    }), 200
