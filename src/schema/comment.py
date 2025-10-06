from xml.etree import ElementTree
from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
from typing import Optional, List
import re
import bleach
from datetime import datetime

from src.schema.user import UserOut

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title']
}


class CommentBase(BaseModel):
    text: str
    parent_id: Optional[int] = None

    @field_validator('text')
    @classmethod
    def validate_text(cls, value: str) -> str:
        clean_text = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )

        if not clean_text.strip():
            raise ValueError("Комментарий не может быть пустым после очистки")

        try:
            wrapped = f"<root>{clean_text}</root>"
            ElementTree.fromstring(wrapped)
        except ElementTree.ParseError:
            raise ValueError("Некорректная структура HTML-тегов")

        return clean_text


class CommentCreate(CommentBase):
    username: str
    email: EmailStr
    homepage: Optional[HttpUrl] = None
    captcha_id: int
    captcha_text: str

    @field_validator('username')
    def validate_username(cls, v):
        if not re.fullmatch(r'[A-Za-z0-9]+', v):
            raise ValueError("Username может содержать только латинские буквы и цифры")
        return v


class CommentPreview(CommentBase):
    username: str
    email: EmailStr
    homepage: Optional[HttpUrl] = None


class CommentOut(CommentBase):
    id: int
    user: UserOut
    created_at: datetime
    replies: List["CommentOut"] = []
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None

    class Config:
        from_attributes = True


