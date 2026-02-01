from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    quips = db.relationship("Quip", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    quip_ups = db.relationship("QuipUp", back_populates="user", cascade="all, delete-orphan")
    comment_ups = db.relationship("CommentUp", back_populates="user", cascade="all, delete-orphan")
    reposts = db.relationship("Repost", back_populates="user", cascade="all, delete-orphan")


class Quip(db.Model):
    __tablename__ = "quips"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    usage_examples = db.Column(db.Text, nullable=True)
    definition = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    author = db.relationship("User", back_populates="quips")
    comments = db.relationship("Comment", back_populates="quip", cascade="all, delete-orphan")
    quip_ups = db.relationship("QuipUp", back_populates="quip", cascade="all, delete-orphan")
    reposts = db.relationship("Repost", back_populates="quip", cascade="all, delete-orphan")


class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quip_id = db.Column(db.Integer, db.ForeignKey("quips.id"), nullable=False)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    author = db.relationship("User", back_populates="comments")
    quip = db.relationship("Quip", back_populates="comments")
    parent = db.relationship("Comment", remote_side=[id], backref="replies")
    comment_ups = db.relationship("CommentUp", back_populates="comment", cascade="all, delete-orphan")


class QuipUp(db.Model):
    __tablename__ = "quip_ups"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    quip_id = db.Column(db.Integer, db.ForeignKey("quips.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship("User", back_populates="quip_ups")
    quip = db.relationship("Quip", back_populates="quip_ups")


class CommentUp(db.Model):
    __tablename__ = "comment_ups"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship("User", back_populates="comment_ups")
    comment = db.relationship("Comment", back_populates="comment_ups")


class Repost(db.Model):
    __tablename__ = "reposts"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    quip_id = db.Column(db.Integer, db.ForeignKey("quips.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship("User", back_populates="reposts")
    quip = db.relationship("Quip", back_populates="reposts")
