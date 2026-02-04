from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.quip_service import QuipService
from app.schemas import QuipCreateSchema
from app.utils.response import APIResponse
from app.utils.errors import ValidationError, NotFoundError, AuthorizationError, ConflictError
from pydantic import ValidationError as PydanticValidationError

bp = Blueprint("quips", __name__)


@bp.route("", methods=["GET"])
def get_feed():
    sort = request.args.get("sort", "smart")
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        raise ValidationError("Page must be a valid integer")
    
    quips = QuipService.get_feed(sort=sort, page=page)
    
    quips_data = [{
        "id": quip.id,
        "user_id": quip.user_id,
        "username": quip.author.username,
        "content": quip.content,
        "definition": quip.definition,
        "usage_examples": quip.usage_examples,
        "created_at": quip.created_at.isoformat(),
        "quip_ups_count": len(quip.quip_ups or []),  # type: ignore
        "comments_count": len(quip.comments or []),  # type: ignore
        "reposts_count": len(quip.reposts or [])  # type: ignore
    } for quip in quips]
    
    return APIResponse.success(data=quips_data)


@bp.route("", methods=["POST"])
@jwt_required()
def create_quip():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        validated_data = QuipCreateSchema(**data)
        content = validated_data.content
        definition = validated_data.definition
        usage_examples = validated_data.usage_examples
    except PydanticValidationError as e:
        raise ValidationError("Validation failed", details={"validation_errors": e.errors()})
    
    try:
        quip = QuipService.create(user_id, content, definition, usage_examples)
        return APIResponse.success(
            data={
                "id": quip.id,
                "user_id": quip.user_id,
                "username": quip.author.username,
                "content": quip.content,
                "definition": quip.definition,
                "usage_examples": quip.usage_examples,
                "created_at": quip.created_at.isoformat()
            },
            message="Quip created successfully",
            status_code=201
        )
    except ValueError as e:
        raise ValidationError(str(e))


@bp.route("/<int:quip_id>", methods=["GET"])
def get_quip(quip_id: int):
    quip = QuipService.get_by_id(quip_id)
    
    if not quip:
        raise NotFoundError("Quip not found")
    
    return APIResponse.success(
        data={
            "id": quip.id,
            "user_id": quip.user_id,
            "username": quip.author.username,
            "content": quip.content,
            "definition": quip.definition,
            "usage_examples": quip.usage_examples,
            "created_at": quip.created_at.isoformat(),
            "quip_ups_count": len(quip.quip_ups or []),  # type: ignore
            "comments_count": len(quip.comments or []),  # type: ignore
            "reposts_count": len(quip.reposts or [])  # type: ignore
        }
    )


@bp.route("/<int:quip_id>", methods=["DELETE"])
@jwt_required()
def delete_quip(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.delete(user_id, quip_id)
        return APIResponse.success(message="Quip deleted successfully")
    except ValueError as e:
        if "not found" in str(e):
            raise NotFoundError(str(e))
        elif "not authorized" in str(e):
            raise AuthorizationError(str(e))
        raise ValidationError(str(e))


@bp.route("/<int:quip_id>/up", methods=["POST"])
@jwt_required()
def add_quip_up(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.add_up(user_id, quip_id)
        return APIResponse.success(message="Upvoted successfully", status_code=201)
    except ValueError as e:
        if "Already upvoted" in str(e):
            raise ConflictError(str(e))
        elif "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))


@bp.route("/<int:quip_id>/up", methods=["DELETE"])
@jwt_required()
def remove_quip_up(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.remove_up(user_id, quip_id)
        return APIResponse.success(message="Upvote removed successfully")
    except ValueError as e:
        if "Not upvoted" in str(e):
            raise ConflictError(str(e))
        elif "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))


@bp.route("/<int:quip_id>/repost", methods=["POST"])
@jwt_required()
def add_repost(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.add_repost(user_id, quip_id)
        return APIResponse.success(message="Reposted successfully", status_code=201)
    except ValueError as e:
        if "Already reposted" in str(e):
            raise ConflictError(str(e))
        elif "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))


@bp.route("/<int:quip_id>/repost", methods=["DELETE"])
@jwt_required()
def remove_repost(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.remove_repost(user_id, quip_id)
        return APIResponse.success(message="Repost removed successfully")
    except ValueError as e:
        if "Not reposted" in str(e):
            raise ConflictError(str(e))
        elif "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))
