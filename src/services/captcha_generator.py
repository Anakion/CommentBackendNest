import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os



class CaptchaGenerator:
    def __init__(self):
        self.width = 200
        self.height = 80
        self.font_size = 35
        self.load_fonts()

    def load_fonts(self):
        """Загружаем доступные шрифты"""
        self.fonts = []
        # Попробуем найти системные шрифты
        font_paths = [
            # Windows
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/times.ttf",
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            # Mac
            "/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Times New Roman.ttf",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, self.font_size)
                    self.fonts.append(font)
                except Exception:
                    continue

        # Если шрифты не найдены, используем стандартный
        if not self.fonts:
            try:
                self.fonts = [ImageFont.load_default()]
            except:
                self.fonts = [None]

    def generate_text(self, length: int = 6) -> str:
        """Генерирует случайный текст для CAPTCHA"""
        characters = string.ascii_uppercase + string.digits
        # Исключаем похожие символы (0/O, 1/I/l и т.д.)
        confusing_chars = {'0', 'O', '1', 'I', 'l'}
        characters = ''.join(c for c in characters if c not in confusing_chars)
        return ''.join(random.choice(characters) for _ in range(length))

    def draw_background(self, image: Image.Image):
        """Рисует фон с шумом"""
        draw = ImageDraw.Draw(image)

        # Заливка фона
        bg_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        draw.rectangle([0, 0, self.width, self.height], fill=bg_color)

        # Случайные линии на фоне
        for _ in range(random.randint(3, 6)):
            line_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            draw.line([x1, y1, x2, y2], fill=line_color, width=random.randint(1, 2))

        # Случайные точки
        for _ in range(random.randint(50, 100)):
            dot_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            draw.point([x, y], fill=dot_color)

    def draw_text(self, image: Image.Image, text: str):
        """Рисует искаженный текст"""
        draw = ImageDraw.Draw(image)

        # Вычисляем общую ширину текста
        total_width = sum(draw.textlength(char, font=random.choice(self.fonts)) for char in text)
        spacing = (self.width - total_width) / (len(text) + 1)

        x = spacing
        for i, char in enumerate(text):
            font = random.choice(self.fonts)
            char_width = draw.textlength(char, font=font)

            # Случайные искажения для каждого символа
            y_offset = random.randint(-5, 5)
            rotation = random.randint(-10, 10)

            # Цвет символа
            text_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))

            # Создаем временное изображение для символа
            char_img = Image.new('RGBA', (int(char_width) + 10, self.font_size + 10), (0, 0, 0, 0))
            char_draw = ImageDraw.Draw(char_img)

            # Рисуем символ
            char_draw.text((5, 5 + y_offset), char, fill=text_color, font=font)

            # Поворачиваем символ
            if rotation != 0:
                char_img = char_img.rotate(rotation, expand=True, resample=Image.BICUBIC)

            # Накладываем символ на основное изображение
            y_pos = (self.height - char_img.height) // 2 + random.randint(-5, 5)
            image.paste(char_img, (int(x), y_pos), char_img)

            x += char_width + spacing

    def apply_distortion(self, image: Image.Image) -> Image.Image:
        """Применяет искажения к изображению"""
        # Wave distortion
        width, height = image.size
        wave_length = random.randint(10, 20)
        amplitude = random.randint(2, 4)

        distorted = Image.new('RGB', (width, height))
        distort_draw = ImageDraw.Draw(distorted)

        for x in range(width):
            for y in range(height):
                # Синусоидальное искажение
                offset_x = int(amplitude * (y / wave_length))
                new_x = (x + offset_x) % width
                pixel = image.getpixel((new_x, y))
                distort_draw.point([x, y], fill=pixel)

        # Размытие
        distorted = distorted.filter(ImageFilter.GaussianBlur(radius=0.5))

        return distorted

    def generate_captcha_image(self, text: str) -> BytesIO:
        """Генерирует CAPTCHA изображение с заданным текстом"""
        # Создаем изображение
        image = Image.new('RGB', (self.width, self.height), color='white')

        # Рисуем фон
        self.draw_background(image)

        # Рисуем текст
        self.draw_text(image, text)

        # Применяем искажения
        image = self.apply_distortion(image)

        # Сохраняем в bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        return img_byte_arr


# Глобальный экземпляр
captcha_generator = CaptchaGenerator()