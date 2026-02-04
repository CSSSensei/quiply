from pydantic import BaseModel, EmailStr, Field, validator
import re
from typing import Optional


class UserRegistrationSchema(BaseModel):
    username: str = Field(..., min_length=5, max_length=20, description="Username must be 5-20 characters")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128, description="Password must be at least 6 characters")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-z0-9_]+$', v):
            raise ValueError('Username can only contain lowercase letters, numbers, and underscores')
        return v


class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=1, description="Username is required")
    password: str = Field(..., min_length=1, description="Password is required")


class UserUpdateSchema(BaseModel):
    bio: Optional[str] = Field(None, max_length=500, description="Bio must be less than 500 characters")


class QuipCreateSchema(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Content must be 1-1000 characters")
    definition: Optional[str] = Field(None, max_length=500, description="Definition must be less than 500 characters")
    usage_examples: Optional[str] = Field(None, max_length=1000, description="Usage examples must be less than 1000 characters")


class QuipUpdateSchema(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000, description="Content must be 1-1000 characters")
    definition: Optional[str] = Field(None, max_length=500, description="Definition must be less than 500 characters")
    usage_examples: Optional[str] = Field(None, max_length=1000, description="Usage examples must be less than 1000 characters")


class CommentCreateSchema(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Comment must be 1-1000 characters")
    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")
