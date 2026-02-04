from flask import Blueprint, request
from app.services.quip_service import QuipService
from app.models import User
from app.utils.response import APIResponse
from app.utils.errors import ValidationError, NotFoundError

bp = Blueprint("users", __name__)


@bp.route("/<string:username>", methods=["GET"])
def get_user_profile(username: str):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        raise NotFoundError("User not found")
    
    total_quip_ups = sum(len(quip.quip_ups or []) for quip in user.quips or [])  # type: ignore
    total_reposts = sum(len(quip.reposts or []) for quip in user.quips or [])  # type: ignore
    
    top_quips = sorted(user.quips or [], key=lambda q: len(q.quip_ups or []), reverse=True)[:3]  # type: ignore
    
    return APIResponse.success(
        data={
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "created_at": user.created_at.isoformat(),
            "stats": {
                "total_quips": len(user.quips or []),  # type: ignore
                "total_quip_ups": total_quip_ups,
                "total_reposts": total_reposts
            },
            "top_quips": [{
                "id": quip.id,
                "content": quip.content,
                "quip_ups_count": len(quip.quip_ups or [])  # type: ignore
            } for quip in top_quips]
        }
    )


@bp.route("/<string:username>/quips", methods=["GET"])
def get_user_quips(username: str):
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        raise ValidationError("Page must be a valid integer")
    
    try:
        quips = QuipService.get_user_quips(username, page=page)
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
    except ValueError as e:
        if "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))


@bp.route("/<string:username>/reposts", methods=["GET"])
def get_user_reposts(username: str):
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        raise ValidationError("Page must be a valid integer")
    
    try:
        quips = QuipService.get_user_reposts(username, page=page)
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
    except ValueError as e:
        if "not found" in str(e):
            raise NotFoundError(str(e))
        raise ValidationError(str(e))
