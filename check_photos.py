# -*- coding: utf-8 -*-
"""
Скрипт проверки фотографий для Telegram бота
Проверяет размеры и формат всех фото из config
"""

import os
from PIL import Image
import config

def check_photo(path, name):
    """Проверка одного фото"""
    if not os.path.exists(path):
        print(f"❌ {name}: ФАЙЛ НЕ НАЙДЕН")
        print(f"   Путь: {path}")
        return False
    
    try:
        with Image.open(path) as img:
            width, height = img.size
            file_size = os.path.getsize(path) / (1024 * 1024)  # MB
            
            # Telegram требования:
            # - Минимум: 1x1 пикселей
            # - Максимум: одна из сторон не больше 10000 пикселей
            # - Размер файла: до 10 МБ
            
            is_ok = True
            issues = []
            
            if width < 1 or height < 1:
                is_ok = False
                issues.append("Размер меньше 1x1 пикселей")
            
            if width > 10000 or height > 10000:
                is_ok = False
                issues.append(f"Размер {width}x{height} (макс 10000 пикселей)")
            
            if file_size > 10:
                is_ok = False
                issues.append(f"Размер файла {file_size:.2f} MB (макс 10 MB)")
            
            if is_ok:
                print(f"✅ {name}: {width}x{height}, {file_size:.2f} MB, {img.format}")
                return True
            else:
                print(f"⚠️ {name}: ПРОБЛЕМА!")
                print(f"   Размер: {width}x{height}")
                print(f"   Файл: {file_size:.2f} MB")
                print(f"   Формат: {img.format}")
                for issue in issues:
                    print(f"   ❌ {issue}")
                return False
                
    except Exception as e:
        print(f"❌ {name}: ОШИБКА ЧТЕНИЯ")
        print(f"   {e}")
        return False


def main():
    print("=" * 60)
    print("ПРОВЕРКА ФОТОГРАФИЙ ДЛЯ TELEGRAM БОТА")
    print("=" * 60)
    print()
    
    all_ok = True
    
    print("📷 Проверка основных фото:")
    print("-" * 60)
    for num, path in config.PHOTOS.items():
        if not check_photo(path, f"Фото {num}"):
            all_ok = False
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✅ ВСЕ ФОТО В ПОРЯДКЕ!")
    else:
        print("⚠️ НАЙДЕНЫ ПРОБЛЕМНЫЕ ФОТО!")
        print()
        print("🔧 Что делать:")
        print("1. Пересохраните проблемные фото в JPEG или PNG")
        print("2. Уменьшите размер, если больше 10000 пикселей")
        print("3. Сожмите файл, если больше 10 МБ")
        print("4. Убедитесь что размер не меньше 1x1 пикселей")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

