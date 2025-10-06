# routes/comments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from typing import Optional, List

from pydantic import EmailStr, HttpUrl

from src.dependency import get_comment_service, get_captcha_service, get_file_service
from src.models.comment import Comment
from src.schema.comment import CommentCreate, CommentOut, CommentPreview
from src.schema.pagination import PaginatedComments
from src.services.comment import CommentService
from src.services.captcha import CaptchaService
from src.services.file import FileService
import os

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentOut)
async def create_comment(
        text: str = Form(...),
        username: str = Form(...),
        email: EmailStr = Form(...),
        homepage: Optional[HttpUrl] = Form(None),
        parent_id: Optional[int] = Form(None),
        captcha_id: int = Form(...),
        captcha_text: str = Form(...),
        image_file: Optional[UploadFile] = File(None),
        text_file: Optional[UploadFile] = File(None),
        comment_service: CommentService = Depends(get_comment_service),
        captcha_service: CaptchaService = Depends(get_captcha_service),
        file_service: FileService = Depends(get_file_service)
):
    # Валидация CAPTCHA
    is_valid_captcha = await captcha_service.validate_captcha(
        captcha_id,
        captcha_text
    )
    if not is_valid_captcha:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверная CAPTCHA"
        )

    # Проверяем что передано не более одного файла
    if image_file and text_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно прикрепить только один файл - изображение или текстовый файл"
        )

    file_data = None
    if image_file:
        file_data = await file_service.save_image(image_file)
    elif text_file:
        file_data = await file_service.save_text_file(text_file)

    # Создаем комментарий
    try:
        comment = await comment_service.create_comment(
            text=text,
            username=username,
            email=str(email),
            homepage=str(homepage) if homepage else None,
            parent_id=parent_id
        )

        # Обновляем информацию о файле если есть
        if file_data:
            comment.file_path = file_data["file_path"]
            comment.file_name = file_data["file_name"]
            comment.file_size = file_data["file_size"]
            comment.file_type = file_data["file_type"]
            if "image_width" in file_data:
                comment.image_width = file_data["image_width"]
                comment.image_height = file_data["image_height"]

            await comment_service.comment_repo.session.commit()
            await comment_service.comment_repo.session.refresh(
                comment,
                attribute_names=['user', 'replies']
            )
        else:
            await comment_service.comment_repo.session.refresh(
                comment,
                attribute_names=['user', 'replies']  # И ЭТО ТОЖЕ!
            )

        return comment

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/preview", response_model=CommentOut)
async def preview_comment(
        comment_data: CommentPreview
):
    """Просмотр комментария без сохранения"""
    # Просто возвращаем данные для просмотра
    return {
        "id": 0,  # Временный ID для просмотра
        "text": comment_data.text,
        "user": {
            "id": 0,
            "username": comment_data.username,
            "email": comment_data.email,
            "homepage": comment_data.homepage,
            "created_at": "2023-01-01T00:00:00"
        },
        "created_at": "2023-01-01T00:00:00",
        "replies": []
    }


@router.get("/", response_model=PaginatedComments)
async def get_comments(
        page: int = Query(1, ge=1),
        per_page: int = Query(25, ge=1, le=100),
        sort_by: str = Query("created_at", regex="^(username|email|created_at)$"),
        order: str = Query("desc", regex="^(asc|desc)$"),
        comment_service: CommentService = Depends(get_comment_service)
):
    """Получение комментариев с пагинацией и сортировкой"""
    comments = await comment_service.get_comments_paginated(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order
    )

    total = await comment_service.comment_repo.get_total_count()
    total_pages = (total + per_page - 1) // per_page

    return PaginatedComments(
        comments=comments,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment(
        comment_id: int,
        comment_service: CommentService = Depends(get_comment_service)
):
    """Получение конкретного комментария с ответами"""
    comment = await comment_service.get_comment_with_replies(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    return comment


@router.get("/{comment_id}/replies", response_model=List[CommentOut])
async def get_comment_replies(
        comment_id: int,
        comment_service: CommentService = Depends(get_comment_service)
):
    """Получения ответа на комментарий"""
    replies = await comment_service.comment_repo.get_replies(comment_id)
    return replies