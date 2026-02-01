from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comment_service import CommentService

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
            "comment_ups_count": len(comment.comment_ups),
            "replies": [serialize_comment(reply) for reply in comment.replies]
        }
    
    return jsonify([serialize_comment(comment) for comment in comments]), 200


@bp.route("/<int:quip_id>/comments", methods=["POST"])
@jwt_required()
def create_comment(quip_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    content = data.get("content")
    parent_id = data.get("parent_id")
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    try:
        comment = CommentService.create(user_id, quip_id, content, parent_id)
        return jsonify({
            "id": comment.id,
            "user_id": comment.user_id,
            "quip_id": comment.quip_id,
            "parent_comment_id": comment.parent_comment_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/comments/<int:comment_id>/up", methods=["POST"])
@jwt_required()
def add_comment_up(comment_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        CommentService.add_up(user_id, comment_id)
        return jsonify({"message": "Upvoted successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/comments/<int:comment_id>/up", methods=["DELETE"])
@jwt_required()
def remove_comment_up(comment_id: int):
    user_id = int(get_jwt_identity())
    
    try:
        CommentService.remove_up(user_id, comment_id)
        return jsonify({"message": "Upvote removed successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
