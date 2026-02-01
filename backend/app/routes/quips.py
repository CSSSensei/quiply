from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.quip_service import QuipService

bp = Blueprint("quips", __name__)


@bp.route("", methods=["GET"])
def get_feed():
    sort = request.args.get("sort", "smart")
    page = int(request.args.get("page", 1))
    
    quips = QuipService.get_feed(sort=sort, page=page)
    
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


@bp.route("", methods=["POST"])
@jwt_required()
def create_quip():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    content = data.get("content")
    definition = data.get("definition")
    usage_examples = data.get("usage_examples")
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    try:
        quip = QuipService.create(user_id, content, definition, usage_examples)
        return jsonify({
            "id": quip.id,
            "user_id": quip.user_id,
            "content": quip.content,
            "definition": quip.definition,
            "usage_examples": quip.usage_examples,
            "created_at": quip.created_at.isoformat()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/<int:quip_id>", methods=["GET"])
def get_quip(quip_id: int):
    quip = QuipService.get_by_id(quip_id)
    
    if not quip:
        return jsonify({"error": "Quip not found"}), 404
    
    return jsonify({
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
    }), 200


@bp.route("/<int:quip_id>/up", methods=["POST"])
@jwt_required()
def add_quip_up(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.add_up(user_id, quip_id)
        return jsonify({"message": "Upvoted successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/<int:quip_id>/up", methods=["DELETE"])
@jwt_required()
def remove_quip_up(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.remove_up(user_id, quip_id)
        return jsonify({"message": "Upvote removed successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/<int:quip_id>/repost", methods=["POST"])
@jwt_required()
def add_repost(quip_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        QuipService.add_repost(user_id, quip_id)
        return jsonify({"message": "Reposted successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
