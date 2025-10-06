from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.comment import Comment


@dataclass
class CommentRepository:
    session: AsyncSession

    async def add(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        result = await self.session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        return result.scalars().first()

    async def get_root_comments(
            self,
            offset: int = 0,
            limit: int = 25,
            sort_by: str = "created_at",
            order: str = "desc"
    ) -> List[Comment]:
        # Рекурсия "план загрузки" при загрузки коментариев
        #  так же загружаются вот эти связанные данные
        def load_replies(level=0):
            if level > 5:  # Защита от бесконечной рекурсии
                return selectinload(Comment.replies)
            return selectinload(Comment.replies).options(
                selectinload(Comment.user), # Загрузить пользователя для ответов
                load_replies(level + 1) # # И для этих ответов тоже загрузить их ответы
            )

        query = (
            select(Comment)
            .where(Comment.parent_id == None)
            .options(
                selectinload(Comment.user),
                load_replies(0)
            )
        )

        # Сортировка
        sort_column = getattr(Comment, sort_by, Comment.created_at)
        if order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_replies(self, parent_id: int) -> List[Comment]:
        result = await self.session.execute(
            select(Comment).where(Comment.parent_id == parent_id)
        )
        return list(result.scalars().all())

    async def get_total_count(self) -> int:
        result = await self.session.execute(
            select(func.count(Comment.id)).where(Comment.parent_id == None)
        )
        return result.scalar()
