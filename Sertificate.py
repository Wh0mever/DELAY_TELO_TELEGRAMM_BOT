from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os


def generate_certificate(full_name, user_id=None, output_dir="certificates"):
    """
    Генерирует персонализированный сертификат
    
    Args:
        full_name (str): Полное имя пользователя (Имя Фамилия)
        user_id (int/str): ID пользователя для уникального имени файла
        output_dir (str): Директория для сохранения сертификатов
    
    Returns:
        str: Путь к созданному сертификату
    """
    
    # Создаем директорию если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Открываем шаблон сертификата
    template_path = "Sertificate.png"
    
    try:
        img = Image.open(template_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Шаблон '{template_path}' не найден! Убедитесь что файл находится в той же папке.")
    
    # Создаем объект для рисования
    draw = ImageDraw.Draw(img)
    
    # Получаем размеры изображения
    img_width, img_height = img.size
    
    # Пытаемся загрузить шрифт (используем разные варианты)
    font_size_name = 45
    font_size_date = 35
    
    try:
        # Для Windows
        font_name = ImageFont.truetype("arial.ttf", font_size_name)
        font_date = ImageFont.truetype("arial.ttf", font_size_date)
    except:
        try:
            # Для Linux
            font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size_name)
            font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size_date)
        except:
            # Если не нашли системные шрифты, используем стандартный
            print("⚠️ Системный шрифт не найден, используется стандартный")
            font_name = ImageFont.load_default()
            font_date = ImageFont.load_default()
    
    # Координаты для имени (верхний темный блок)
    # Примерные координаты по центру верхнего блока
    name_y = 232
    
    # Вычисляем ширину текста для центрирования
    bbox_name = draw.textbbox((0, 0), full_name, font=font_name)
    text_width_name = bbox_name[2] - bbox_name[0]
    name_x = (img_width - text_width_name) // 2
    
    # Рисуем имя (белый цвет)
    draw.text((name_x, name_y), full_name, fill=(255, 255, 255), font=font_name)
    
    # Формируем дату
    current_date = datetime.now()
    date_text = current_date.strftime("%d.%m.%Y")
    
    # Координаты для даты (нижний темный блок)
    date_y = 507
    
    # Вычисляем ширину текста даты для центрирования
    bbox_date = draw.textbbox((0, 0), date_text, font=font_date)
    text_width_date = bbox_date[2] - bbox_date[0]
    date_x = (img_width - text_width_date) // 2
    
    # Рисуем дату (белый цвет)
    draw.text((date_x, date_y), date_text, fill=(255, 255, 255), font=font_date)
    
    # Формируем имя выходного файла
    if user_id:
        output_filename = f"certificate_{user_id}_{current_date.strftime('%Y%m%d_%H%M%S')}.png"
    else:
        # Убираем пробелы из имени для имени файла
        safe_name = full_name.replace(" ", "_")
        output_filename = f"certificate_{safe_name}_{current_date.strftime('%Y%m%d_%H%M%S')}.png"
    
    output_path = os.path.join(output_dir, output_filename)
    
    # Сохраняем сертификат
    img.save(output_path, quality=95)
    
    print(f"✅ Сертификат успешно создан: {output_path}")
    return output_path


# Функция для интеграции с SQLite
def generate_certificate_from_db(cursor, user_id):
    """
    Генерирует сертификат используя данные из базы данных
    
    Args:
        cursor: Курсор SQLite
        user_id: ID пользователя в базе данных
    
    Returns:
        str: Путь к созданному сертификату или None если пользователь не найден
    """
    
    # Получаем данные пользователя из БД
    cursor.execute("SELECT first_name, last_name FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        first_name, last_name = result
        full_name = f"{first_name} {last_name}" if last_name else first_name
        
        return generate_certificate(full_name, user_id)
    else:
        print(f"❌ Пользователь с ID {user_id} не найден в базе данных")
        return None


# Пример использования
if __name__ == "__main__":
    print("=" * 60)
    print("🎓 ГЕНЕРАТОР СЕРТИФИКАТОВ")
    print("=" * 60)
    
    # Пример 1: Простое использование
    try:
        certificate_path = generate_certificate("Наташа ДелайТело")
        print(f"\n📄 Сертификат сохранен: {certificate_path}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    
    # Пример 2: С указанием user_id
    try:
        certificate_path = generate_certificate("Иван Иванов", user_id=12345)
        print(f"\n📄 Сертификат сохранен: {certificate_path}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✨ Готово!")
    print("=" * 60)