from dataclasses import dataclass
from typing import Optional, List

from src.core.websocket import ConnectionManager
from src.models.comment import Comment
from src.repositories.comment import CommentRepository
from src.repositories.user import UserRepository
from src.schema.comment import CommentOut


@dataclass
class CommentService:
    comment_repo: CommentRepository
    user_repo: UserRepository
    websocket_manager: ConnectionManager

    async def create_comment(
            self,
            text: str,
            username: str,
            email: str,
            homepage: Optional[str] = None,
            parent_id: Optional[int] = None
    ) -> Comment:
        # Создаем/получаем пользователя
        user = await self.user_repo.get_or_create(username, email, homepage)

        # Создаем комментарий
        comment = Comment(
            text=text,
            user_id=user.id,
            parent_id=parent_id
        )

        saved_comment = await self.comment_repo.add(comment)

        # Загружаем связи для WebSocket
        await self.comment_repo.session.refresh(saved_comment)
        await self.comment_repo.session.refresh(saved_comment.user)

        # Отправляем уведомление через WebSocket
        comment_out = CommentOut.model_validate(saved_comment, from_attributes=True)
        await self.websocket_manager.broadcast_new_comment(comment_out)

        return saved_comment


    async def get_comments_paginated(
            self,
            page: int = 1,
            per_page: int = 25,
            sort_by: str = "created_at",
            order: str = "desc"
    ) -> List[Comment]:
        offset = (page - 1) * per_page
        return await self.comment_repo.get_root_comments(offset, per_page, sort_by, order)

    async def get_comment_with_replies(self, comment_id: int) -> Optional[Comment]:
        return await self.comment_repo.get_by_id(comment_id)