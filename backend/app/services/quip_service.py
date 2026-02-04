from datetime import datetime
from typing import Optional
from sqlalchemy import func, desc
from app import db
from app.models import Quip, QuipUp, Comment, Repost, User
from app.utils.logger import setup_logger, log_info, log_error, log_warning

logger = setup_logger()


class QuipService:
    @staticmethod
    def create(user_id: int, content: str, definition: Optional[str] = None,
               usage_examples: Optional[str] = None) -> Quip:
        log_info(logger, "Creating quip", {"user_id": user_id, "has_content": bool(content)})
        
        if not content or not content.strip():
            log_warning(logger, "Quip creation failed - empty content", {"user_id": user_id})
            raise ValueError("Content cannot be empty")
        
        quip = Quip()
        quip.user_id = user_id
        quip.content = content.strip()
        quip.definition = definition.strip() if definition else None
        quip.usage_examples = usage_examples.strip() if usage_examples else None
        
        try:
            db.session.add(quip)
            db.session.commit()
            log_info(logger, "Quip created successfully", {"quip_id": quip.id, "user_id": user_id})
            return quip
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "quip_creation", "user_id": user_id})
            raise ValueError("Failed to create quip")
    
    @staticmethod
    def get_by_id(quip_id: int) -> Optional[Quip]:
        log_info(logger, "Fetching quip by ID", {"quip_id": quip_id})
        quip = Quip.query.get(quip_id)
        if quip:
            log_info(logger, "Quip found", {"quip_id": quip_id, "user_id": quip.user_id})
        else:
            log_warning(logger, "Quip not found", {"quip_id": quip_id})
        return quip
    
    @staticmethod
    def delete(user_id: int, quip_id: int) -> None:
        log_info(logger, "Deleting quip", {"user_id": user_id, "quip_id": quip_id})
        
        quip = Quip.query.get(quip_id)
        if not quip:
            log_warning(logger, "Delete failed - quip not found", {"quip_id": quip_id})
            raise ValueError("Quip not found")
        if quip.user_id != user_id:
            log_warning(logger, "Delete failed - unauthorized", {"user_id": user_id, "quip_id": quip_id, "quip_owner": quip.user_id})
            raise ValueError("Not authorized to delete this quip")
        
        try:
            db.session.delete(quip)
            db.session.commit()
            log_info(logger, "Quip deleted successfully", {"quip_id": quip_id, "user_id": user_id})
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "quip_deletion", "quip_id": quip_id, "user_id": user_id})
            raise ValueError("Failed to delete quip")
    
    @staticmethod
    def get_feed(sort: str = "smart", page: int = 1, per_page: int = 20) -> list[Quip]:
        log_info(logger, "Fetching quip feed", {"sort": sort, "page": page, "per_page": per_page})
        
        try:
            quips = Quip.query.order_by(desc(Quip.created_at)).paginate(
                page=page, per_page=per_page, error_out=False
            ).items
            log_info(logger, "Feed fetched successfully", {"count": len(quips), "page": page})
            return quips
        except Exception as e:
            log_error(logger, e, {"operation": "feed_fetch", "sort": sort, "page": page})
            return []
    
    @staticmethod
    def add_up(user_id: int, quip_id: int) -> QuipUp:
        log_info(logger, "Adding quip upvote", {"user_id": user_id, "quip_id": quip_id})
        
        existing = QuipUp.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if existing:
            log_warning(logger, "Upvote failed - already upvoted", {"user_id": user_id, "quip_id": quip_id})
            raise ValueError("Already upvoted")
        
        quip_up = QuipUp()
        quip_up.user_id = user_id
        quip_up.quip_id = quip_id
        
        try:
            db.session.add(quip_up)
            db.session.commit()
            log_info(logger, "Quip upvoted successfully", {"user_id": user_id, "quip_id": quip_id})
            return quip_up
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "quip_upvote", "user_id": user_id, "quip_id": quip_id})
            raise ValueError("Failed to upvote quip")
    
    @staticmethod
    def remove_up(user_id: int, quip_id: int) -> None:
        log_info(logger, "Removing quip upvote", {"user_id": user_id, "quip_id": quip_id})
        
        quip_up = QuipUp.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if not quip_up:
            log_warning(logger, "Remove upvote failed - not upvoted", {"user_id": user_id, "quip_id": quip_id})
            raise ValueError("Not upvoted")
        
        try:
            db.session.delete(quip_up)
            db.session.commit()
            log_info(logger, "Quip upvote removed successfully", {"user_id": user_id, "quip_id": quip_id})
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "quip_upvote_removal", "user_id": user_id, "quip_id": quip_id})
            raise ValueError("Failed to remove upvote")
    
    @staticmethod
    def add_repost(user_id: int, quip_id: int) -> Repost:
        log_info(logger, "Adding repost", {"user_id": user_id, "quip_id": quip_id})
        
        existing = Repost.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if existing:
            log_warning(logger, "Repost failed - already reposted", {"user_id": user_id, "quip_id": quip_id})
            raise ValueError("Already reposted")
        
        repost = Repost()
        repost.user_id = user_id
        repost.quip_id = quip_id
        
        try:
            db.session.add(repost)
            db.session.commit()
            log_info(logger, "Repost added successfully", {"user_id": user_id, "quip_id": quip_id})
            return repost
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "repost_addition", "user_id": user_id, "quip_id": quip_id})
            raise ValueError("Failed to repost")
    
    @staticmethod
    def remove_repost(user_id: int, quip_id: int) -> None:
        log_info(logger, "Removing repost", {"user_id": user_id, "quip_id": quip_id})
        
        repost = Repost.query.filter_by(user_id=user_id, quip_id=quip_id).first()
        if not repost:
            log_warning(logger, "Remove repost failed - not reposted", {"user_id": user_id, "quip_id": quip_id})
            raise ValueError("Not reposted")
        
        try:
            db.session.delete(repost)
            db.session.commit()
            log_info(logger, "Repost removed successfully", {"user_id": user_id, "quip_id": quip_id})
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "repost_removal", "user_id": user_id, "quip_id": quip_id})
            raise ValueError("Failed to remove repost")
    
    @staticmethod
    def get_user_quips(username: str, page: int = 1, per_page: int = 20) -> list[Quip]:
        log_info(logger, "Fetching user quips", {"username": username, "page": page})
        
        user = User.query.filter_by(username=username).first()
        if not user:
            log_warning(logger, "User quips fetch failed - user not found", {"username": username})
            raise ValueError("User not found")
        
        try:
            quips = Quip.query.filter_by(user_id=user.id).order_by(
                desc(Quip.created_at)
            ).paginate(page=page, per_page=per_page, error_out=False).items
            log_info(logger, "User quips fetched successfully", {"username": username, "count": len(quips)})
            return quips
        except Exception as e:
            log_error(logger, e, {"operation": "user_quips_fetch", "username": username, "page": page})
            return []
    
    @staticmethod
    def get_user_reposts(username: str, page: int = 1, per_page: int = 20) -> list[Quip]:
        log_info(logger, "Fetching user reposts", {"username": username, "page": page})
        
        user = User.query.filter_by(username=username).first()
        if not user:
            log_warning(logger, "User reposts fetch failed - user not found", {"username": username})
            raise ValueError("User not found")
        
        try:
            reposts = Repost.query.filter_by(user_id=user.id).order_by(
                desc(Repost.created_at)
            ).paginate(page=page, per_page=per_page, error_out=False).items
            
            quips = [repost.quip for repost in reposts]
            log_info(logger, "User reposts fetched successfully", {"username": username, "count": len(quips)})
            return quips
        except Exception as e:
            log_error(logger, e, {"operation": "user_reposts_fetch", "username": username, "page": page})
            return []
