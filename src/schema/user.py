from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
import re
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    homepage: Optional[HttpUrl] = None


    @field_validator('username')
    def validate_username(cls, v):
        if not re.fullmatch(r'[A-Za-z0-9]+', v):
            raise ValueError("Username может содержать только латинские буквы и цифры")
        return v


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True