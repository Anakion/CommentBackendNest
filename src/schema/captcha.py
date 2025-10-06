from datetime import datetime

from pydantic import BaseModel, field_validator
import re

class CaptchaBase(BaseModel):
    text: str

    @field_validator('text')
    def validate_text(cls, v):
        if not re.fullmatch(r'[A-Za-z0-9]+', v):
            raise ValueError("CAPTCHA может содержать только латинские буквы и цифры")
        if len(v) != 6:
            raise ValueError("CAPTCHA должна быть длиной 6 символов")
        return v

class CaptchaCreate(CaptchaBase):
    pass

class CaptchaOut(CaptchaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
