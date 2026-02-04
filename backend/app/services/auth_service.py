from typing import Optional
import bcrypt
from flask_jwt_extended import create_access_token
from app import db
from app.models import User
from app.utils.logger import setup_logger, log_info, log_error, log_warning

logger = setup_logger()


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    
    @staticmethod
    def register(username: str, email: str, password: str) -> User:
        log_info(logger, "User registration attempt", {"username": username, "email": email})
        
        if User.query.filter_by(username=username).first():
            log_warning(logger, "Registration failed - username already exists", {"username": username})
            raise ValueError("Username already exists")
        
        if User.query.filter_by(email=email).first():
            log_warning(logger, "Registration failed - email already exists", {"email": email})
            raise ValueError("Email already exists")
        
        password_hash = AuthService.hash_password(password)
        user = User()
        user.username = username
        user.email = email
        user.password_hash = password_hash
        
        try:
            db.session.add(user)
            db.session.commit()
            log_info(logger, "User registered successfully", {"user_id": user.id, "username": username})
            return user
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "user_registration", "username": username})
            raise ValueError("Registration failed")
    
    @staticmethod
    def login(username: str, password: str) -> str:
        log_info(logger, "Login attempt", {"username": username})
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not AuthService.verify_password(password, user.password_hash):
            log_warning(logger, "Login failed - invalid credentials", {"username": username})
            raise ValueError("Invalid credentials")
        
        token = create_access_token(identity=str(user.id))
        log_info(logger, "Login successful", {"user_id": user.id, "username": username})
        return token
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        log_info(logger, "Fetching user by ID", {"user_id": user_id})
        user = User.query.get(user_id)
        if user:
            log_info(logger, "User found", {"user_id": user_id, "username": user.username})
        else:
            log_warning(logger, "User not found", {"user_id": user_id})
        return user
    
    @staticmethod
    def update_user(user_id: int, bio: Optional[str] = None) -> User:
        log_info(logger, "Updating user", {"user_id": user_id, "has_bio": bio is not None})
        
        user = User.query.get(user_id)
        
        if not user:
            log_warning(logger, "Update failed - user not found", {"user_id": user_id})
            raise ValueError("User not found")
        
        if bio is not None:
            user.bio = bio
        
        try:
            db.session.commit()
            log_info(logger, "User updated successfully", {"user_id": user_id})
            return user
        except Exception as e:
            db.session.rollback()
            log_error(logger, e, {"operation": "user_update", "user_id": user_id})
            raise ValueError("Update failed")
