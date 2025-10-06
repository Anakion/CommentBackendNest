# routes/captcha.py
from fastapi import APIRouter, Depends
from fastapi.responses import Response
import io
from src.schema.captcha import CaptchaOut
from src.services.captcha import CaptchaService
from src.dependency import get_captcha_service
import random
from PIL import Image, ImageDraw, ImageFont
import string

router = APIRouter(prefix="/captcha", tags=["captcha"])


@router.post("/", response_model=CaptchaOut)
async def create_captcha(
        captcha_service: CaptchaService = Depends(get_captcha_service)
):
    """Создание новой CAPTCHA"""
    return await captcha_service.generate_captcha()


@router.get("/{captcha_id}/image")
async def get_captcha_image(
        captcha_id: int,
        captcha_service: CaptchaService = Depends(get_captcha_service)
):
    """Получение CAPTCHA в виде изображения"""
    # Здесь должна быть логика получения текста CAPTCHA по ID
    # и генерации изображения
    # Пока заглушка

    # Генерируем простое изображение с текстом
    width, height = 200, 80
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Простой текст для демонстрации
    text = "CAPTCHA"
    # В реальности здесь должен быть текст из БД

    draw.text((50, 30), text, fill='black')

    # Конвертируем в bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return Response(content=img_byte_arr, media_type="image/png")