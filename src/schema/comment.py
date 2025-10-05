from pydantic import BaseModel, EmailStr, HttpUrl, validator, field_validator
from typing import Optional, List
import re
import bleach
from datetime import datetime

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title']
}

class CommentBase(BaseModel):
    text: str
    parent_id: Optional[int] = None

    @validator('text')
    def validate_text(cls, v):
        clean_text = bleach.clean(
            v,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
        if not clean_text.strip():
            raise ValueError("Комментарий не может быть пустым после очистки")
        return clean_text

class CommentCreate(CommentBase):
    username: str
    email: EmailStr
    homepage: Optional[HttpUrl] = None
    captcha: str

    @field_validator('username')
    def validate_username(cls, v):
        if not re.fullmatch(r'[A-Za-z0-9]+', v):
            raise ValueError("Username может содержать только латинские буквы и цифры")
        return v

    @field_validator('captcha')
    def validate_captcha(cls, v):
        if not re.fullmatch(r'[A-Za-z0-9]+', v):
            raise ValueError("CAPTCHA должна содержать только латинские буквы и цифры")
        if len(v) != 6:
            raise ValueError("CAPTCHA должна быть длиной 6 символов")
        return v

class CommentOut(CommentBase):
    id: int
    user_id: int
    username: str
    created_at: datetime
    replies: List["CommentOut"] = []

    class Config:
        orm_mode = True
