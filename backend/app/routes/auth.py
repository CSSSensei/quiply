from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.schemas import UserRegistrationSchema, UserLoginSchema, UserUpdateSchema
from pydantic import ValidationError

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    try:
        validated_data = UserRegistrationSchema(**data)
        username = validated_data.username
        email = validated_data.email
        password = validated_data.password
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400
    
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
    
    try:
        validated_data = UserLoginSchema(**data)
        username = validated_data.username
        password = validated_data.password
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400
    
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


@bp.route("/me", methods=["PUT"])
@jwt_required()
def update_current_user():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        validated_data = UserUpdateSchema(**data)
        bio = validated_data.bio
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400
    
    try:
        user = AuthService.update_user(user_id, bio)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "created_at": user.created_at.isoformat()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
