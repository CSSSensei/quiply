from datetime import datetime
from typing import Optional
from sqlalchemy import func, desc
from app import db
from app.models import Quip, QuipUp, Comment, Repost, User


class QuipService:
    @staticmethod
    def create(user_id: int, content: str, definition: Optional[str] = None, 
               usage_examples: Optional[str] = None) -> Quip:
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        quip = Quip(
            user_id=user_id,
            content=content.strip(),
            definition=definition.strip() if definition else None,
            usage_examples=usage_examples.strip() if usage_examples else None
        )
        
        db.session.add(quip)
        db.session.commit()
        
        return quip
    
    @staticmethod
    def get_by_id(quip_id: int) -> Optional[Quip]:
        return Quip.query.get(quip_id)
    
    @staticmethod
    def delete(user_id: int, quip_id: int) -> None:
        quip = Quip.query.get(quip_id)
        if not quip:
            raise ValueError("Quip not found")
        if quip.user_id != user_id:
            raise ValueError("Not authorized to delete this quip")
        
        db.session.delete(quip)
        db.session.commit()
    
    @staticmethod
    def get_feed(sort: str = "smart", page: int = 1, per_page: int = 20) -> list[Quip]:
        return Quip.query.order_by(desc(Quip.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        ).items
    
    @staticmethod
    def add_up(user_id: int, quip_id: int) -> QuipUp:
        existing = QuipUp.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if existing:
            raise ValueError("Already upvoted")
        
        quip_up = QuipUp(user_id=user_id, quip_id=quip_id)
        db.session.add(quip_up)
        db.session.commit()
        
        return quip_up
    
    @staticmethod
    def remove_up(user_id: int, quip_id: int) -> None:
        quip_up = QuipUp.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if not quip_up:
            raise ValueError("Not upvoted")
        
        db.session.delete(quip_up)
        db.session.commit()
    
    @staticmethod
    def add_repost(user_id: int, quip_id: int) -> Repost:
        existing = Repost.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if existing:
            raise ValueError("Already reposted")
        
        repost = Repost(user_id=user_id, quip_id=quip_id)
        db.session.add(repost)
        db.session.commit()
        
        return repost
    
    @staticmethod
    def remove_repost(user_id: int, quip_id: int) -> None:
        repost = Repost.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if not repost:
            raise ValueError("Not reposted")
        
        db.session.delete(repost)
        db.session.commit()
    
    @staticmethod
    def get_user_quips(username: str, page: int = 1, per_page: int = 20) -> list[Quip]:
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        
        return Quip.query.filter_by(user_id=user.id).order_by(
            desc(Quip.created_at)
        ).paginate(page=page, per_page=per_page, error_out=False).items
    
    @staticmethod
    def get_user_reposts(username: str, page: int = 1, per_page: int = 20) -> list[Quip]:
        user = User.query.filter_by(username=username).first()
        if not user:
            raise ValueError("User not found")
        
        reposts = Repost.query.filter_by(user_id=user.id).order_by(
            desc(Repost.created_at)
        ).paginate(page=page, per_page=per_page, error_out=False).items
        
        return [repost.quip for repost in reposts]
