from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.captcha import Captcha


@dataclass
class CaptchaRepository:
    session: AsyncSession

    async def create(self, captcha: Captcha) -> Captcha:
        self.session.add(captcha)
        await self.session.commit()
        await self.session.refresh(captcha)
        return captcha

    async def get_by_id(self, captcha_id: int) -> Optional[Captcha]:
        """Получает CAPTCHA по ID"""
        result = await self.session.execute(
            select(Captcha).where(Captcha.id == captcha_id)
        )
        return result.scalars().first()

    async def get_valid_captcha(self, captcha_id: int, text: str) -> Optional[Captcha]:
        # CAPTCHA действительна 10 минут
        time_threshold = datetime.utcnow() - timedelta(minutes=10)

        result = await self.session.execute(
            select(Captcha).where(
                and_(
                    Captcha.id == captcha_id,
                    Captcha.text == text,
                    Captcha.created_at >= time_threshold,
                    Captcha.is_used == False
                )
            )
        )
        return result.scalars().first()

    async def mark_as_used(self, captcha_id: int):
        captcha = await self.session.get(Captcha, captcha_id)
        if captcha:
            captcha.is_used = True
            await self.session.commit()