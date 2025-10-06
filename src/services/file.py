# services.py (дополняем FileService)
import io
import os
from dataclasses import dataclass

from PIL import Image
import aiofiles
from fastapi import UploadFile, HTTPException
import uuid


@dataclass
class FileService:
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
    MAX_IMAGE_SIZE = 1024 * 1024  # 1MB
    MAX_TEXT_SIZE = 100 * 1024  # 100KB
    UPLOAD_DIR = "uploads"

    def __post_init__(self):
        os.makedirs(f"{self.UPLOAD_DIR}/images", exist_ok=True)
        os.makedirs(f"{self.UPLOAD_DIR}/texts", exist_ok=True)

    async def save_image(self, file: UploadFile) -> dict:
        """Сохраняет изображение с ресайзом до 320x240"""
        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(400, "Недопустимый формат изображения")

        # Читаем файл
        content = await file.read()
        if len(content) > self.MAX_IMAGE_SIZE:
            raise HTTPException(400, "Размер изображения слишком большой")

        # Генерируем уникальное имя
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = f"{self.UPLOAD_DIR}/images/{filename}"

        # Обрабатываем изображение
        try:
            with Image.open(io.BytesIO(content)) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # Ресайз с сохранением размерами
                img.thumbnail((320, 240), Image.Resampling.LANCZOS)

                # Сохраняем
                img.save(file_path, 'JPEG' if file_ext.lower() == 'jpg' else file_ext.upper())

                return {
                    "file_path": file_path,
                    "file_name": file.filename,
                    "file_size": os.path.getsize(file_path),
                    "file_type": "image",
                    "image_width": img.width,
                    "image_height": img.height
                }
        except Exception as e:
            raise HTTPException(400, f"Ошибка обработки изображения: {str(e)}")

    async def save_text_file(self, file: UploadFile) -> dict:
        """Сохраняет текстовый файл"""
        if file.content_type != 'text/plain':
            raise HTTPException(400, "Файл должен быть текстовым (.txt)")

        content = await file.read()
        if len(content) > self.MAX_TEXT_SIZE:
            raise HTTPException(400, "Размер текстового файла превышает 100KB")

        # Проверяем что это действительно текст
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(400, "Файл должен быть в UTF-8 кодировке")

        # Сохраняем
        filename = f"{uuid.uuid4()}.txt"
        file_path = f"{self.UPLOAD_DIR}/texts/{filename}"

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        return {
            "file_path": file_path,
            "file_name": file.filename,
            "file_size": len(content),
            "file_type": "text"
        }

    async def validate_file(self, file: UploadFile) -> bool:
        """Валидация файла перед сохранением"""
        if file.content_type.startswith('image/'):
            return await self.validate_image(file)
        elif file.content_type == 'text/plain':
            return await self.validate_text_file(file)
        return False

    async def validate_image(self, file: UploadFile) -> bool:
        content = await file.read()
        await file.seek(0)  # Возвращаем указатель для повторного чтения

        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            return False
        if len(content) > self.MAX_IMAGE_SIZE:
            return False
        return True

    async def validate_text_file(self, file: UploadFile) -> bool:
        content = await file.read()
        await file.seek(0)

        if file.content_type != 'text/plain':
            return False
        if len(content) > self.MAX_TEXT_SIZE:
            return False
        try:
            content.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False