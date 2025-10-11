# -*- coding: utf-8 -*-
"""
Конфигурационный файл для Табата-Интенсив бота
"""

import os

# Токен бота
BOT_TOKEN = "8357062293:AAFChKKrpKLIU_cSSTVF3QV4WeDk5Bf4nYg"

# Пути к директориям
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "Табата-Интенсив")
CERTIFICATES_DIR = os.path.join(BASE_DIR, "certificates")

# Пути к медиа-файлам
PHOTOS = {
    1: os.path.join(MEDIA_DIR, "Фото 1.png"),
    2: os.path.join(MEDIA_DIR, "Фото 2.png"),
    3: os.path.join(MEDIA_DIR, "Фото 3.png"),
    4: os.path.join(MEDIA_DIR, "Фото 4.png"),
    5: os.path.join(MEDIA_DIR, "Фото 5.png"),
    6: os.path.join(MEDIA_DIR, "Фото 6.png"),
    7: os.path.join(MEDIA_DIR, "Фото 7.png"),
    8: os.path.join(MEDIA_DIR, "Фото 8.png"),
    9: os.path.join(MEDIA_DIR, "Фото 9.png"),
    10: os.path.join(MEDIA_DIR, "фото 10.jpg"),
    11: os.path.join(MEDIA_DIR, "фото 11.png"),
    12: os.path.join(MEDIA_DIR, "фото 12.png"),
}

# Пути к PDF файлам
PDFS = {
    "guide": os.path.join(MEDIA_DIR, "Гайд Интенсива ДелайТело.pdf"),
    "trackers": os.path.join(MEDIA_DIR, "Трекеры Чат Реалити.pdf"),
    "demo_calendar": os.path.join(MEDIA_DIR, "ДемоКалендарь Интенсив.pdf"),
}

# ID канала с видео
VIDEO_CHANNEL_ID = -1003006477133

# Message ID для каждого видео в канале (реальные ID из t.me/c/3006477133/X)
VIDEO_MESSAGE_IDS = {
    1: 2,      # День 1 - Табата (https://t.me/c/3006477133/2)
    3: 3,      # День 3 - Руки и пресс (https://t.me/c/3006477133/3)
    5: 4,      # День 5 - Ягодицы (https://t.me/c/3006477133/4)
    "7_yoga": 5,     # День 7 - Йога (https://t.me/c/3006477133/5)
    "7_dance": 6,    # День 7 - Танцы Бруно Марс (https://t.me/c/3006477133/6)
    8: 7,      # День 8 - Руки и пресс (https://t.me/c/3006477133/7)
    10: 8,     # День 10 - Ягодицы (https://t.me/c/3006477133/8)
    12: 9,     # День 12 - Табата (https://t.me/c/3006477133/9)
    14: 10,    # День 14 - Танцы (https://t.me/c/3006477133/10)
    15: 11,    # День 15 - Руки и пресс (https://t.me/c/3006477133/11)
    17: 12,    # День 17 - Ягодицы (https://t.me/c/3006477133/12)
    19: 13,    # День 19 - Табата (https://t.me/c/3006477133/13)
    "14_yoga": 14,   # День 14 - Йога (https://t.me/c/3006477133/14)
}

# Message ID для фото из канала (для проблемных фото с PHOTO_INVALID_DIMENSIONS)
# Если фото есть в этом словаре, оно будет переслано из канала вместо локального файла
PHOTO_MESSAGE_IDS = {
    1: 15,     # Фото 1 - День 0 (https://t.me/c/3006477133/15)
    11: 16,    # Фото 11 - День 20 (https://t.me/c/3006477133/16)
    12: 16,    # Фото 12 - День 4 (https://t.me/c/3006477133/16)
    # Добавьте сюда другие проблемные фото при необходимости
}

# Настройки планировщика
REMINDER_TIME = "09:00"  # Время напоминания о новом дне

# Путь к шаблону сертификата
CERTIFICATE_TEMPLATE = os.path.join(BASE_DIR, "Sertificate.png")

# База данных
DATABASE_PATH = os.path.join(BASE_DIR, "tabata_bot.db")

# Промокод для финала
PROMO_CODE = "TABATA25"
PROMO_DISCOUNT = "25%"
PROMO_DESCRIPTION = "Скидка 25% на индивидуальную программу с планом питания на 28 дней по тарифу 'Супервумен'"

# Создаем директории если их нет
os.makedirs(CERTIFICATES_DIR, exist_ok=True)

