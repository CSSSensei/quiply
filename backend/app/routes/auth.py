from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.schemas import UserRegistrationSchema, UserLoginSchema, UserUpdateSchema
from app.utils.response import APIResponse
from app.utils.errors import ValidationError, AuthenticationError, NotFoundError
from pydantic import ValidationError as PydanticValidationError

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    try:
        validated_data = UserRegistrationSchema(**data)
        username = validated_data.username
        email = validated_data.email
        password = validated_data.password
    except PydanticValidationError as e:
        raise ValidationError("Validation failed", details={"validation_errors": e.errors()})
    
    try:
        user = AuthService.register(username, email, password)
        return APIResponse.success(
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            message="User registered successfully",
            status_code=201
        )
    except ValueError as e:
        if "already exists" in str(e):
            from app.utils.errors import ConflictError
            raise ConflictError(str(e))
        raise ValidationError(str(e))


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    try:
        validated_data = UserLoginSchema(**data)
        username = validated_data.username
        password = validated_data.password
    except PydanticValidationError as e:
        raise ValidationError("Validation failed", details={"validation_errors": e.errors()})
    
    try:
        token = AuthService.login(username, password)
        return APIResponse.success(
            data={"token": token},
            message="Login successful"
        )
    except ValueError as e:
        raise AuthenticationError(str(e))


@bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = AuthService.get_user_by_id(user_id)
    
    if not user:
        raise NotFoundError("User not found")
    
    return APIResponse.success(
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "bio": user.bio,
            "created_at": user.created_at.isoformat()
        }
    )


@bp.route("/me", methods=["PUT"])
@jwt_required()
def update_current_user():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        validated_data = UserUpdateSchema(**data)
        bio = validated_data.bio
    except PydanticValidationError as e:
        raise ValidationError("Validation failed", details={"validation_errors": e.errors()})
    
    try:
        user = AuthService.update_user(user_id, bio)
        return APIResponse.success(
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "bio": user.bio,
                "created_at": user.created_at.isoformat()
            },
            message="Profile updated successfully"
        )
    except ValueError as e:
        raise ValidationError(str(e))
