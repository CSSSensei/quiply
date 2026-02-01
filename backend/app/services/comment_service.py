from typing import Optional
from sqlalchemy import desc
from app import db
from app.models import Comment, CommentUp, Quip


class CommentService:
    @staticmethod
    def create(user_id: int, quip_id: int, content: str, 
               parent_id: Optional[int] = None) -> Comment:
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        quip = Quip.query.get(quip_id)
        if not quip:
            raise ValueError("Quip not found")
        
        if parent_id:
            parent = Comment.query.get(parent_id)
            if not parent or parent.quip_id != quip_id:
                raise ValueError("Invalid parent comment")
        
        comment = Comment(
            user_id=user_id,
            quip_id=quip_id,
            parent_comment_id=parent_id,
            content=content.strip()
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return comment
    
    @staticmethod
    def get_quip_comments(quip_id: int) -> list[Comment]:
        return Comment.query.filter_by(
            quip_id=quip_id, 
            parent_comment_id=None
        ).order_by(desc(Comment.created_at)).all()
    
    @staticmethod
    def add_up(user_id: int, comment_id: int) -> CommentUp:
        existing = CommentUp.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if existing:
            raise ValueError("Already upvoted")
        
        comment_up = CommentUp(user_id=user_id, comment_id=comment_id)
        db.session.add(comment_up)
        db.session.commit()
        
        return comment_up
    
    @staticmethod
    def remove_up(user_id: int, comment_id: int) -> None:
        comment_up = CommentUp.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if not comment_up:
            raise ValueError("Not upvoted")
        
        db.session.delete(comment_up)
        db.session.commit()
