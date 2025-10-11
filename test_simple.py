# -*- coding: utf-8 -*-
print("=== START TEST ===")

try:
    from PIL import Image, ImageDraw, ImageFont
    print("PIL imported OK")
except Exception as e:
    print(f"PIL error: {e}")
    exit(1)

try:
    from datetime import datetime
    print("datetime imported OK")
except Exception as e:
    print(f"datetime error: {e}")
    exit(1)

try:
    import os
    print("os imported OK")
except Exception as e:
    print(f"os error: {e}")
    exit(1)

print("Opening template...")
try:
    img = Image.open("Sertificate.png")
    print(f"Template opened: {img.size}")
except Exception as e:
    print(f"Template error: {e}")
    exit(1)

print("Creating certificate...")
try:
    draw = ImageDraw.Draw(img)
    
    # Шрифт
    try:
        font_name = ImageFont.truetype("arialbd.ttf", 60)
        print("Font: Arial Bold")
    except:
        font_name = ImageFont.truetype("arial.ttf", 60)
        print("Font: Arial")
    
    # Цвета
    color_name = (226, 65, 107)
    color_date = (0, 0, 0)
    
    # Имя
    full_name = "Тестовое Имя"
    bbox = draw.textbbox((0, 0), full_name, font=font_name)
    text_width = bbox[2] - bbox[0]
    name_x = (img.size[0] - text_width) // 2
    name_y = 205
    
    draw.text((name_x, name_y), full_name, fill=color_name, font=font_name)
    print(f"Name drawn at ({name_x}, {name_y})")
    
    # Дата
    date_text = datetime.now().strftime("%d.%m.%Y")
    font_date = ImageFont.truetype("arial.ttf", 32)
    draw.text((165, 508), date_text, fill=color_date, font=font_date)
    print(f"Date drawn: {date_text}")
    
    # Сохранение
    output_path = "test_simple_cert.png"
    img.save(output_path, quality=95)
    print(f"SAVED: {output_path}")
    
except Exception as e:
    print(f"Drawing error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("=== SUCCESS ===")

