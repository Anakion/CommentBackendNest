from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


@dataclass
class UserRepository:
    session: AsyncSession

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(self, username: str, email: str, homepage: Optional[str] = None) -> User:
        existing_user = await self.get_by_username(username)
        if existing_user:
            return existing_user

        existing_user = await self.get_by_email(email)
        if existing_user:
            return existing_user

        # Создаем нового
        new_user = User(username=username, email=email, homepage=homepage)
        return await self.create(new_user)