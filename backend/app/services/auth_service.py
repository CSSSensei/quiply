from typing import Optional
import bcrypt
from flask_jwt_extended import create_access_token
from app import db
from app.models import User


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    
    @staticmethod
    def register(username: str, email: str, password: str) -> User:
        if User.query.filter_by(username=username).first():
            raise ValueError("Username already exists")
        
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")
        
        password_hash = AuthService.hash_password(password)
        user = User(username=username, email=email, password_hash=password_hash)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def login(username: str, password: str) -> str:
        user = User.query.filter_by(username=username).first()
        
        if not user or not AuthService.verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        return create_access_token(identity=str(user.id))
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        return User.query.get(user_id)
