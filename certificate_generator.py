# -*- coding: utf-8 -*-
"""
Генератор сертификатов для бота
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import config


def generate_certificate(full_name: str, user_id: int) -> str:
    """
    Генерирует персонализированный сертификат
    
    Args:
        full_name (str): Полное имя пользователя (Имя Фамилия)
        user_id (int): ID пользователя для уникального имени файла
    
    Returns:
        str: Путь к созданному сертификату
    """
    
    # Создаем директорию если её нет
    if not os.path.exists(config.CERTIFICATES_DIR):
        os.makedirs(config.CERTIFICATES_DIR)
    
    # Открываем шаблон сертификата
    template_path = config.CERTIFICATE_TEMPLATE
    
    try:
        img = Image.open(template_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Шаблон '{template_path}' не найден!")
    
    # Создаем объект для рисования
    draw = ImageDraw.Draw(img)
    
    # Получаем размеры изображения
    img_width, img_height = img.size
    
    # === НАСТРОЙКА ШРИФТОВ (ЖИРНЫЕ!) ===
    font_size_name = 60  # Крупный шрифт для имени
    font_size_date = 32  # Средний шрифт для даты
    
    try:
        # Пробуем Arial Bold (жирный) для Windows
        font_name = ImageFont.truetype("arialbd.ttf", font_size_name)
        font_date = ImageFont.truetype("arialbd.ttf", font_size_date)
        print("✅ Шрифт: Arial Bold")
    except:
        try:
            # Обычный Arial если нет Bold
            font_name = ImageFont.truetype("arial.ttf", font_size_name)
            font_date = ImageFont.truetype("arial.ttf", font_size_date)
            print("✅ Шрифт: Arial")
        except:
            try:
                # Для Linux
                font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_name)
                font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_date)
                print("✅ Шрифт: DejaVu Sans Bold")
            except:
                # Если не нашли системные шрифты, используем стандартный
                print("⚠️ Системный шрифт не найден, используется стандартный")
                font_name = ImageFont.load_default()
                font_date = ImageFont.load_default()
    
    # === ЦВЕТА ===
    # КРАСНЫЙ цвет для имени (как заголовок "СЕРТИФИКАТ" на шаблоне)
    color_name = (226, 65, 107)  # #E2416B
    # ЧЕРНЫЙ цвет для даты
    color_date = (0, 0, 0)
    
    # === КООРДИНАТЫ ДЛЯ ИМЕНИ ===
    # Имя должно быть СТРОГО ПО ЦЕНТРУ белой рамки
    name_y = 210  # Вертикальная позиция
    name_x = img_width // 2  # Горизонтально - точно по центру
    
    # Рисуем имя (КРАСНЫМ ЖИРНЫМ) с якорем по центру
    # anchor='mm' означает middle-middle: центр текста = координаты
    draw.text((name_x, name_y), full_name, fill=color_name, font=font_name, anchor='mm')
    print(f"✅ Имя нарисовано: {full_name} (центр: {name_x}, {name_y})")
    
    # === КООРДИНАТЫ ДЛЯ ДАТЫ ===
    current_date = datetime.now()
    date_text = current_date.strftime("%d.%m.%Y")
    
    date_y = 508  # Вертикальная позиция
    date_x = 165  # Горизонтальная позиция (после текста "Дата выдачи:")
    
    # Рисуем дату (ЧЕРНЫМ ЖИРНЫМ)
    draw.text((date_x, date_y), date_text, fill=color_date, font=font_date)
    print(f"✅ Дата нарисована: {date_text} ({date_x}, {date_y})")
    
    # Формируем имя выходного файла
    output_filename = f"certificate_{user_id}_{current_date.strftime('%Y%m%d_%H%M%S')}.png"
    output_path = os.path.join(config.CERTIFICATES_DIR, output_filename)
    
    # Сохраняем сертификат
    img.save(output_path, quality=95)
    
    print(f"✅ Сертификат успешно создан: {output_path}")
    return output_path

