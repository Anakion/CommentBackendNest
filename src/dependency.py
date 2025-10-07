from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.websocket import connection_manager, ConnectionManager
from src.db.session import get_db
from src.repositories.captcha import CaptchaRepository
from src.repositories.comment import CommentRepository
from src.repositories.user import UserRepository
from src.services.captcha import CaptchaService
from src.services.comment import CommentService
from src.services.file import FileService
from src.services.user import UserService


# Репозитории
async def get_comment_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> CommentRepository:
    return CommentRepository(db)

async def get_user_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)

async def get_captcha_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> CaptchaRepository:
    return CaptchaRepository(db)

# Сервисы
async def get_comment_service(
    comment_repo: Annotated[CommentRepository, Depends(get_comment_repository)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> CommentService:
    return CommentService(comment_repo, user_repo, connection_manager)

async def get_websocket_manager() -> ConnectionManager:
    return connection_manager

async def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repo)

async def get_file_service() -> FileService:
    return FileService()

async def get_captcha_service(
    captcha_repo: Annotated[CaptchaRepository, Depends(get_captcha_repository)]
) -> CaptchaService:
    return CaptchaService(captcha_repo)