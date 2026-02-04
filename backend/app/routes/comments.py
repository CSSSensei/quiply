from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comment_service import CommentService
from app.schemas import CommentCreateSchema
from app.utils.response import APIResponse
from app.utils.errors import ValidationError, NotFoundError, ConflictError
from pydantic import ValidationError as PydanticValidationError

bp = Blueprint("comments", __name__)


@bp.route("/<int:quip_id>/comments", methods=["GET"])
def get_comments(quip_id: int):
    comments = CommentService.get_quip_comments(quip_id)
    
    def serialize_comment(comment):
        return {
            "id": comment.id,
            "user_id": comment.user_id,
            "username": comment.author.username,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "comment_ups_count": len(comment.comment_ups or []),  # type: ignore
            "replies": [serialize_comment(reply) for reply in comment.replies or []]
        }
    
    comments_data = [serialize_comment(comment) for comment in comments]
    return APIResponse.success(data=comments_data)


@bp.route("/<int:quip_id>/comments", methods=["POST"])
@jwt_required()
def create_comment(quip_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        validated_data = CommentCreateSchema(**data)
        content = validated_data.content
        parent_id = validated_data.parent_id
    except PydanticValidationError as e:
        raise ValidationError("Validation failed", details={"validation_errors": e.errors()})
    
    try:
        comment = CommentService.create(user_id, quip_id, content, parent_id)
        return APIResponse.success(
            data={
                "id": comment.id,
                "user_id": comment.user_id,
                "quip_id": comment.quip_id,
                "parent_comment_id": comment.parent_comment_id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat()
            },
            message="Comment created successfully",
            status_code=201
        )
    except ValueError as e:
        if "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))


@bp.route("/comments/<int:comment_id>/up", methods=["POST"])
@jwt_required()
def add_comment_up(comment_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        CommentService.add_up(user_id, comment_id)
        return APIResponse.success(message="Upvoted successfully", status_code=201)
    except ValueError as e:
        if "Already upvoted" in str(e):
            raise ConflictError(str(e))
        elif "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))


@bp.route("/comments/<int:comment_id>/up", methods=["DELETE"])
@jwt_required()
def remove_comment_up(comment_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        CommentService.remove_up(user_id, comment_id)
        return APIResponse.success(message="Upvote removed successfully")
    except ValueError as e:
        if "Not upvoted" in str(e):
            raise ConflictError(str(e))
        elif "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))
