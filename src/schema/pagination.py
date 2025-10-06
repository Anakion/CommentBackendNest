# Пагинация и сортировка
from typing import List

from pydantic import field_validator, BaseModel

from src.schema.comment import CommentOut


class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 25
    sort_by: str = "created_at"  # username, email, created_at
    order: str = "desc"  # asc, desc

    @field_validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be greater than 0")
        return v

    @field_validator('per_page')
    def validate_per_page(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Per page must be between 1 and 100")
        return v

    @field_validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['username', 'email', 'created_at']
        if v not in allowed_fields:
            raise ValueError(f"Sort by must be one of {allowed_fields}")
        return v

    @field_validator('order')
    def validate_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError("Order must be 'asc' or 'desc'")
        return v

class PaginatedComments(BaseModel):
    comments: List[CommentOut]
    total: int
    page: int
    per_page: int
    total_pages: int