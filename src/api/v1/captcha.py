# routes/captcha.py
from http.client import HTTPException

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
    image_bytes = await captcha_service.get_captcha_image(captcha_id)

    if not image_bytes:
        raise HTTPException(status_code=404, detail="CAPTCHA not found")

    return Response(
        content=image_bytes.getvalue(),
        media_type="image/png",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )