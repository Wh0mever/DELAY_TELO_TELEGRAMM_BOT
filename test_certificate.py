# -*- coding: utf-8 -*-
"""
Тестовый скрипт генерации сертификата
С правильными координатами и цветами
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os


def generate_certificate_test(full_name, output_path="test_certificate.png"):
    """
    Генерирует персонализированный сертификат
    
    Args:
        full_name (str): Полное имя пользователя (Имя Фамилия)
        output_path (str): Путь для сохранения сертификата
    
    Returns:
        str: Путь к созданному сертификату
    """
    
    # Открываем шаблон сертификата
    template_path = "Sertificate.png"
    
    try:
        img = Image.open(template_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Шаблон '{template_path}' не найден!")
    
    # Создаем объект для рисования
    draw = ImageDraw.Draw(img)
    
    # Получаем размеры изображения
    img_width, img_height = img.size
    print(f"📐 Размер изображения: {img_width}x{img_height}")
    
    # === НАСТРОЙКА ШРИФТОВ ===
    
    # Шрифт для имени (красный, жирный, крупный)
    font_size_name = 60
    try:
        # Пробуем жирный Arial
        font_name = ImageFont.truetype("arialbd.ttf", font_size_name)
        print(f"✅ Шрифт для имени: Arial Bold {font_size_name}")
    except:
        try:
            # Обычный Arial
            font_name = ImageFont.truetype("arial.ttf", font_size_name)
            print(f"✅ Шрифт для имени: Arial {font_size_name}")
        except:
            font_name = ImageFont.load_default()
            print(f"⚠️ Используется стандартный шрифт для имени")
    
    # Шрифт для даты (черный, жирный)
    font_size_date = 32
    try:
        font_date = ImageFont.truetype("arialbd.ttf", font_size_date)
        print(f"✅ Шрифт для даты: Arial Bold {font_size_date}")
    except:
        try:
            font_date = ImageFont.truetype("arial.ttf", font_size_date)
            print(f"✅ Шрифт для даты: Arial {font_size_date}")
        except:
            font_date = ImageFont.load_default()
            print(f"⚠️ Используется стандартный шрифт для даты")
    
    # === ЦВЕТА ===
    # Красный цвет для имени (яркий розово-красный как на сертификате)
    color_name = (226, 65, 107)  # #E2416B - цвет заголовка "СЕРТИФИКАТ"
    
    # Черный цвет для даты
    color_date = (0, 0, 0)
    
    # === КООРДИНАТЫ ДЛЯ ИМЕНИ (верхний красный прямоугольник) ===
    # По фото: имя должно быть СТРОГО ПО ЦЕНТРУ белой рамки
    # Y-координата: примерно 200-220 от верха
    name_y = 210
    
    
    # X-координата: ТОЧНО по центру изображения
    name_x = img_width // 2
    
    print(f"\n👤 Имя: {full_name}")
    print(f"   Координаты центра: ({name_x}, {name_y})")
    print(f"   Ширина изображения: {img_width}")
    print(f"   Цвет: RGB{color_name}")
    
    # Рисуем имя (КРАСНЫМ жирным) с якорем по центру
    # anchor='mm' = middle-middle (центр текста совпадает с координатами)
    draw.text((name_x, name_y), full_name, fill=color_name, font=font_name, anchor='mm')
    
    # === КООРДИНАТЫ ДЛЯ ДАТЫ (нижний красный прямоугольник) ===
    # По фото: дата слева внизу, после текста "Дата выдачи:"
    # Y-координата: примерно 505-520 от верха
    date_y = 508
    
    # Формируем дату
    current_date = datetime.now()
    date_text = current_date.strftime("%d.%m.%Y")
    
    # Вычисляем ширину текста даты
    bbox_date = draw.textbbox((0, 0), date_text, font=font_date)
    text_width_date = bbox_date[2] - bbox_date[0]
    text_height_date = bbox_date[3] - bbox_date[1]
    
    # Дата по центру нижнего блока (или чуть левее если есть надпись "Дата выдачи:")
    # Я вижу что на сертификате есть текст "Дата выдачи:", поэтому дата должна быть чуть правее
    date_x = 165  # Примерная X-координата для даты
    
    print(f"\n📅 Дата: {date_text}")
    print(f"   Координаты: ({date_x}, {date_y})")
    print(f"   Размер текста: {text_width_date}x{text_height_date}")
    print(f"   Цвет: RGB{color_date}")
    
    # Рисуем дату (ЧЕРНЫМ жирным)
    draw.text((date_x, date_y), date_text, fill=color_date, font=font_date)
    
    # === СОХРАНЕНИЕ ===
    img.save(output_path, quality=95)
    
    print(f"\n✅ Сертификат успешно создан: {output_path}")
    return output_path


# === ТЕСТИРОВАНИЕ ===
if __name__ == "__main__":
    print("=" * 70)
    print("🎓 ТЕСТОВЫЙ ГЕНЕРАТОР СЕРТИФИКАТА")
    print("=" * 70)
    print()
    
    # Тест 1: Только имя
    print("📝 Тест 1: Только имя")
    try:
        cert_path = generate_certificate_test("Наташа")
        print(f"✅ Сертификат создан: {cert_path}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "-" * 70 + "\n")
    
    # Тест 2: Имя и фамилия
    print("📝 Тест 2: Имя и фамилия")
    try:
        cert_path = generate_certificate_test("Анна Иванова", "test_certificate_2.png")
        print(f"✅ Сертификат создан: {cert_path}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "-" * 70 + "\n")
    
    # Тест 3: Длинное имя
    print("📝 Тест 3: Длинное имя")
    try:
        cert_path = generate_certificate_test("Екатерина Александрова", "test_certificate_3.png")
        print(f"✅ Сертификат создан: {cert_path}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 70)
    print("✨ ГОТОВО! Проверьте созданные сертификаты:")
    print("   - test_certificate.png")
    print("   - test_certificate_2.png")
    print("   - test_certificate_3.png")
    print()
    print("💡 Если координаты не идеальны, измените:")
    print("   - name_y (строка 68) - для вертикального положения имени")
    print("   - date_x (строка 94) - для горизонтального положения даты")
    print("   - date_y (строка 81) - для вертикального положения даты")
    print("=" * 70)

