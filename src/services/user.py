from dataclasses import dataclass
from typing import Optional

from src.models.user import User
from src.repositories.user import UserRepository


@dataclass
class UserService:
    user_repo: UserRepository

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)