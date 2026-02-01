from flask import Blueprint, request, jsonify
from app.services.quip_service import QuipService
from app.models import User

bp = Blueprint("users", __name__)


@bp.route("/<string:username>", methods=["GET"])
def get_user_profile(username: str):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    total_quip_ups = sum(len(quip.quip_ups) for quip in user.quips)
    total_reposts = sum(len(quip.reposts) for quip in user.quips)
    
    top_quips = sorted(user.quips, key=lambda q: len(q.quip_ups), reverse=True)[:3]
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "created_at": user.created_at.isoformat(),
        "stats": {
            "total_quips": len(user.quips),
            "total_quip_ups": total_quip_ups,
            "total_reposts": total_reposts
        },
        "top_quips": [{
            "id": quip.id,
            "content": quip.content,
            "quip_ups_count": len(quip.quip_ups)
        } for quip in top_quips]
    }), 200


@bp.route("/<string:username>/quips", methods=["GET"])
def get_user_quips(username: str):
    page = int(request.args.get("page", 1))
    
    try:
        quips = QuipService.get_user_quips(username, page=page)
        return jsonify([{
            "id": quip.id,
            "user_id": quip.user_id,
            "username": quip.author.username,
            "content": quip.content,
            "definition": quip.definition,
            "usage_examples": quip.usage_examples,
            "created_at": quip.created_at.isoformat(),
            "quip_ups_count": len(quip.quip_ups),
            "comments_count": len(quip.comments),
            "reposts_count": len(quip.reposts)
        } for quip in quips]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/<string:username>/reposts", methods=["GET"])
def get_user_reposts(username: str):
    page = int(request.args.get("page", 1))
    
    try:
        quips = QuipService.get_user_reposts(username, page=page)
        return jsonify([{
            "id": quip.id,
            "user_id": quip.user_id,
            "username": quip.author.username,
            "content": quip.content,
            "definition": quip.definition,
            "usage_examples": quip.usage_examples,
            "created_at": quip.created_at.isoformat(),
            "quip_ups_count": len(quip.quip_ups),
            "comments_count": len(quip.comments),
            "reposts_count": len(quip.reposts)
        } for quip in quips]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
