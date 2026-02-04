from typing import Optional
from sqlalchemy import desc
from app import db
from app.models import Comment, CommentUp, Quip
from app.utils.logger import setup_logger, log_info, log_error, log_warning

logger = setup_logger()


class CommentService:
    @staticmethod
    def create(user_id: int, quip_id: int, content: str,
               parent_id: Optional[int] = None) -> Comment:
        log_info(logger, "Creating comment", {"user_id": user_id, "quip_id": quip_id, "parent_id": parent_id})
        
        if not content or not content.strip():
            log_warning(logger, "Comment creation failed - empty content", {"user_id": user_id, "quip_id": quip_id})
            raise ValueError("Content cannot be empty")
        
        quip = Quip.query.get(quip_id)
        if not quip:
            log_warning(logger, "Comment creation failed - quip not found", {"quip_id": quip_id})
            raise ValueError("Quip not found")
        
        if parent_id:
            parent = Comment.query.get(parent_id)
            if not parent or parent.quip_id != quip_id:
                log_warning(logger, "Comment creation failed - invalid parent", {"parent_id": parent_id, "quip_id": quip_id})
                raise ValueError("Invalid parent comment")
        
        comment = Comment()
        comment.user_id = user_id
        comment.quip_id = quip_id
        comment.parent_comment_id = parent_id
        comment.content = content.strip()
        
        try:
            db.session.add(comment)
            db.session.commit()
            log_info(logger, "Comment created successfully", {"comment_id": comment.id, "user_id": user_id, "quip_id": quip_id})
            return comment
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "comment_creation", "user_id": user_id, "quip_id": quip_id})
            raise ValueError("Failed to create comment")
    
    @staticmethod
    def get_quip_comments(quip_id: int) -> list[Comment]:
        log_info(logger, "Fetching quip comments", {"quip_id": quip_id})
        
        try:
            comments = Comment.query.filter_by(
                quip_id=quip_id,
                parent_comment_id=None
            ).order_by(desc(Comment.created_at)).all()
            log_info(logger, "Quip comments fetched successfully", {"quip_id": quip_id, "count": len(comments)})
            return comments
        except Exception as e:
            log_error(logger, e, {"operation": "quip_comments_fetch", "quip_id": quip_id})
            return []
    
    @staticmethod
    def add_up(user_id: int, comment_id: int) -> CommentUp:
        log_info(logger, "Adding comment upvote", {"user_id": user_id, "comment_id": comment_id})
        
        existing = CommentUp.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if existing:
            log_warning(logger, "Comment upvote failed - already upvoted", {"user_id": user_id, "comment_id": comment_id})
            raise ValueError("Already upvoted")
        
        comment_up = CommentUp()
        comment_up.user_id = user_id
        comment_up.comment_id = comment_id
        
        try:
            db.session.add(comment_up)
            db.session.commit()
            log_info(logger, "Comment upvoted successfully", {"user_id": user_id, "comment_id": comment_id})
            return comment_up
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "comment_upvote", "user_id": user_id, "comment_id": comment_id})
            raise ValueError("Failed to upvote comment")
    
    @staticmethod
    def remove_up(user_id: int, comment_id: int) -> None:
        log_info(logger, "Removing comment upvote", {"user_id": user_id, "comment_id": comment_id})
        
        comment_up = CommentUp.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if not comment_up:
            log_warning(logger, "Remove comment upvote failed - not upvoted", {"user_id": user_id, "comment_id": comment_id})
            raise ValueError("Not upvoted")
        
        try:
            db.session.delete(comment_up)
            db.session.commit()
            log_info(logger, "Comment upvote removed successfully", {"user_id": user_id, "comment_id": comment_id})
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "comment_upvote_removal", "user_id": user_id, "comment_id": comment_id})
            raise ValueError("Failed to remove upvote")
