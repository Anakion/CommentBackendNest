import secrets
import string
from dataclasses import dataclass

from src.models.captcha import Captcha
from src.repositories.captcha import CaptchaRepository


@dataclass
class CaptchaService:
    captcha_repo: CaptchaRepository

    async def generate_captcha(self) -> Captcha:
        # Генерирую случайную строку из 6 символов
        characters = string.ascii_uppercase + string.digits
        captcha_text = ''.join(secrets.choice(characters) for _ in range(6))

        captcha = Captcha(text=captcha_text)
        return await self.captcha_repo.create(captcha)

    async def validate_captcha(self, captcha_id: int, text: str) -> bool:
        captcha = await self.captcha_repo.get_valid_captcha(captcha_id, text)
        if captcha:
            await self.captcha_repo.mark_as_used(captcha_id)
            return True
        return False