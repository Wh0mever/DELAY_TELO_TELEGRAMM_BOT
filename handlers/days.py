# -*- coding: utf-8 -*-
"""
Обработчик всех дней интенсива
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import content
import keyboards
from database import db
from certificate_generator import generate_certificate

router = Router()


def split_long_message(text: str, max_length: int = 4000) -> list:
    """Разбивает длинное сообщение на части
    
    Args:
        text: текст для разбиения
        max_length: максимальная длина одной части (по умолчанию 4000, оставляем запас от лимита 4096)
    
    Returns:
        список частей текста
    """
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Разбиваем по параграфам (двойной перенос строки)
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # Если параграф + текущая часть меньше лимита
        if len(current_part) + len(paragraph) + 2 <= max_length:
            if current_part:
                current_part += "\n\n" + paragraph
            else:
                current_part = paragraph
        else:
            # Сохраняем текущую часть
            if current_part:
                parts.append(current_part)
            
            # Если параграф сам больше лимита, разбиваем его
            if len(paragraph) > max_length:
                # Разбиваем по предложениям
                sentences = paragraph.split('. ')
                temp_part = ""
                for sentence in sentences:
                    if len(temp_part) + len(sentence) + 2 <= max_length:
                        if temp_part:
                            temp_part += ". " + sentence
                        else:
                            temp_part = sentence
                    else:
                        if temp_part:
                            parts.append(temp_part)
                        temp_part = sentence
                if temp_part:
                    current_part = temp_part
            else:
                current_part = paragraph
    
    # Добавляем последнюю часть
    if current_part:
        parts.append(current_part)
    
    return parts


async def send_before_after_photos(message_obj, user_id: int):
    """
    Отправляет фото ДО и ПОСЛЕ с мотивационным текстом
    """
    # Получаем фото из БД
    photo_before = db.get_photo(user_id, "before")
    photo_after = db.get_photo(user_id, "after")
    
    if not photo_before or not photo_after:
        print(f"⚠️ Фото ДО или ПОСЛЕ не найдены для user {user_id}")
        return
    
    try:
        # Определяем тип объекта
        if hasattr(message_obj, 'message'):
            # Это CallbackQuery
            chat = message_obj.message
        else:
            # Это Message
            chat = message_obj
        
        # Отправляем заголовок
        await chat.answer(
            "📸 <b>ТВОЯ ТРАНСФОРМАЦИЯ</b>\n\n"
            "Взгляни, что изменилось за эти 21 день! 💫",
            parse_mode="HTML"
        )
        
        # Отправляем фото ДО
        await chat.answer_photo(
            photo=photo_before['file_id'],
            caption="📸 <b>ФОТО ДО</b>\n\n"
                    f"Дата: {photo_before['uploaded_at'][:10]}",
            parse_mode="HTML"
        )
        
        # Отправляем фото ПОСЛЕ
        await chat.answer_photo(
            photo=photo_after['file_id'],
            caption="📸 <b>ФОТО ПОСЛЕ</b>\n\n"
                    f"Дата: {photo_after['uploaded_at'][:10]}",
            parse_mode="HTML"
        )
        
        # Мотивационный текст
        motivation_text = """✨ <b>ТЫ ЭТО СДЕЛАЛА!</b>

Смотри на эти фотографии и гордись собой! 🌟

За эти 21 день ты:
💪 Укрепила своё тело
🔥 Зажгла внутреннюю силу
💚 Влюбилась в движение
✨ Стала увереннее в себе

Это не просто "до" и "после". Это твоя история силы, дисциплины и любви к себе.

<b>Ты красавица! Продолжай двигаться вперёд! 🚀</b>

С любовью и гордостью за тебя,
💗 Наташа ДелайТело"""
        
        await chat.answer(motivation_text, parse_mode="HTML")
        
        print(f"✅ Фото ДО/ПОСЛЕ отправлены user {user_id}")
        
    except Exception as e:
        print(f"⚠️ Ошибка отправки фото ДО/ПОСЛЕ: {e}")


async def send_long_message(message_obj, text: str, reply_markup=None):
    """Отправка длинного сообщения с автоматическим разбиением на части
    
    Args:
        message_obj: Message или CallbackQuery
        text: текст для отправки
        reply_markup: клавиатура (добавляется только к последнему сообщению)
    """
    parts = split_long_message(text)
    
    for i, part in enumerate(parts):
        # Клавиатура только в последнем сообщении
        keyboard = reply_markup if i == len(parts) - 1 else None
        
        # Правильно определяем тип объекта
        if hasattr(message_obj, 'message'):
            # Это CallbackQuery
            await message_obj.message.answer(part, reply_markup=keyboard)
        else:
            # Это Message
            await message_obj.answer(part, reply_markup=keyboard)


async def send_video_from_channel(message: Message, day_key):
    """Отправка видео из канала"""
    try:
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=config.VIDEO_CHANNEL_ID,
            message_id=config.VIDEO_MESSAGE_IDS[day_key]
        )
    except Exception as e:
        await message.answer(f"⚠️ Видео временно недоступно")
        print(f"Ошибка отправки видео день {day_key}: {e}")


async def send_photo_safe(message_obj, photo_path, caption, reply_markup=None, photo_num=None):
    """Безопасная отправка фото с обработкой ошибок
    
    Args:
        message_obj: Message или CallbackQuery
        photo_path: путь к локальному файлу
        caption: подпись к фото
        reply_markup: клавиатура
        photo_num: номер фото (1-12) для проверки в PHOTO_MESSAGE_IDS
    """
    import os
    
    # Проверяем, есть ли фото в канале (для проблемных фото)
    if photo_num and photo_num in config.PHOTO_MESSAGE_IDS:
        try:
            # Отправляем из канала
            message_id = config.PHOTO_MESSAGE_IDS[photo_num]
            
            # Правильно определяем тип объекта
            if hasattr(message_obj, 'message'):
                # Это CallbackQuery
                bot = message_obj.bot
                chat_id = message_obj.message.chat.id
            else:
                # Это Message
                bot = message_obj.bot
                chat_id = message_obj.chat.id
            
            # Если caption слишком длинный (>1024), отправляем отдельно
            if len(caption) > 1000:  # Запас от лимита 1024
                print(f"⚠️ Caption слишком длинный ({len(caption)} символов), отправляем отдельно")
                
                # Отправляем фото без caption
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=config.VIDEO_CHANNEL_ID,
                    message_id=message_id
                )
                
                # Отправляем текст отдельно с разбиением если нужно
                await send_long_message(message_obj, caption, reply_markup=reply_markup)
                
                print(f"✅ Фото {photo_num} отправлено из канала + текст отдельно")
                return
            else:
                # Caption нормальной длины, отправляем вместе
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=config.VIDEO_CHANNEL_ID,
                    message_id=message_id,
                    caption=caption,
                    reply_markup=reply_markup
                )
                print(f"✅ Фото {photo_num} отправлено из канала (message_id={message_id})")
                return
            
        except Exception as e:
            error_msg = str(e)
            if "message caption is too long" in error_msg or "MESSAGE_TOO_LONG" in error_msg:
                print(f"⚠️ Caption слишком длинный при отправке из канала")
                print(f"   Отправляем фото без caption и текст отдельно...")
                
                try:
                    # Отправляем фото без caption
                    await bot.copy_message(
                        chat_id=chat_id,
                        from_chat_id=config.VIDEO_CHANNEL_ID,
                        message_id=message_id
                    )
                    
                    # Отправляем текст отдельно
                    await send_long_message(message_obj, caption, reply_markup=reply_markup)
                    
                    print(f"✅ Фото {photo_num} отправлено из канала + текст отдельно (fallback)")
                    return
                except Exception as e2:
                    print(f"⚠️ Ошибка fallback отправки: {e2}")
            else:
                print(f"⚠️ Ошибка отправки фото {photo_num} из канала: {e}")
                print(f"   Попытка отправить локальный файл...")
    
    # Проверяем существование локального файла
    if not os.path.exists(photo_path):
        print(f"⚠️ ФАЙЛ НЕ НАЙДЕН: {photo_path}")
        # Отправляем текст с автоматическим разбиением
        await send_long_message(message_obj, caption, reply_markup=reply_markup)
        return
    
    try:
        # Отправляем локальный файл
        photo = FSInputFile(photo_path)
        
        # Если caption слишком длинный, отправляем отдельно
        if len(caption) > 1000:  # Запас от лимита 1024 для caption
            print(f"⚠️ Caption слишком длинный ({len(caption)} символов), отправляем отдельно")
            
            # Отправляем фото без caption
            if hasattr(message_obj, 'message'):
                # Это CallbackQuery
                await message_obj.message.answer_photo(photo=photo)
            else:
                # Это Message
                await message_obj.answer_photo(photo=photo)
            
            # Отправляем текст отдельно
            await send_long_message(message_obj, caption, reply_markup=reply_markup)
            
            print(f"✅ Фото отправлено из локального файла + текст отдельно")
        else:
            # Caption нормальной длины
            if hasattr(message_obj, 'message'):
                # Это CallbackQuery
                await message_obj.message.answer_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup
                )
            else:
                # Это Message
                await message_obj.answer_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup
                )
            print(f"✅ Фото отправлено из локального файла: {photo_path}")
        
    except Exception as e:
        # Если фото недоступно (неправильные размеры, формат и т.д.)
        error_msg = str(e)
        if "PHOTO_INVALID_DIMENSIONS" in error_msg:
            print(f"⚠️ НЕПРАВИЛЬНЫЕ РАЗМЕРЫ ФОТО: {photo_path}")
            print(f"   Telegram требует: 1x1 - 10000x10000 пикселей")
            print(f"   💡 Загрузите это фото на канал и добавьте в config.PHOTO_MESSAGE_IDS")
        elif "MESSAGE_TOO_LONG" in error_msg or "message caption is too long" in error_msg:
            print(f"⚠️ СЛИШКОМ ДЛИННЫЙ CAPTION: {len(caption)} символов (лимит 1024)")
        else:
            print(f"⚠️ Ошибка отправки фото {photo_path}: {e}")
        
        # Отправляем текст (с автоматическим разбиением если слишком длинный)
        await send_long_message(message_obj, caption, reply_markup=reply_markup)


class PhotoStates(StatesGroup):
    """Состояния для загрузки фото"""
    waiting_for_photo_after = State()


# === НЕДЕЛЯ 1 ===

@router.callback_query(F.data == "start_day_1")
async def start_day_1(callback: CallbackQuery):
    """День 1 - Музыкальная Табата"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Отправляем контент недели 1
    await send_photo_safe(
        callback,
        config.PHOTOS[4],
        content.WEEK_1_START,
        reply_markup=keyboards.get_week_start_keyboard(1),
        photo_num=4
    )
    
    # Отправляем день 1
    await callback.message.answer(content.DAY_1_TEXT)
    
    # Пересылаем видео из канала
    await send_video_from_channel(callback.message, 1)
    
    await callback.message.answer(
        "📹 День 1 - Табата",
        reply_markup=keyboards.get_workout_keyboard(1)
    )
    
    db.update_user_day(user_id, 1)


@router.callback_query(F.data.startswith("completed_workout_"))
async def completed_workout(callback: CallbackQuery):
    """Обработка выполнения тренировки"""
    await callback.answer("✅ Отлично! Тренировка зафиксирована")
    
    user_id = callback.from_user.id
    day = int(callback.data.split("_")[-1])
    
    # Отмечаем выполнение
    db.mark_day_completed(user_id, day, 'workout')
    
    # Проверяем ачивки
    await check_and_give_achievements(callback.message, user_id, day)
    
    # Отправляем сообщение после выполнения
    if day == 1:
        await callback.message.answer(
            content.DAY_1_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 5:
        await callback.message.answer(
            content.DAY_5_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 7:
        # День 7 - Завершение недели 1
        await callback.message.answer(content.WEEK_1_CONCLUSION)
        if db.add_achievement(user_id, "week_1"):
            await callback.message.answer(content.get_achievement_message("week_1"))
        if db.add_achievement(user_id, "alone"):
            await callback.message.answer(content.get_achievement_message("alone"))
        await callback.message.answer(
            "Готова ко второй неделе?",
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 8:
        await callback.message.answer(
            content.DAY_8_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 10:
        await callback.message.answer(
            content.DAY_10_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 12:
        await callback.message.answer(
            content.DAY_12_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 14:
        # День 14 - Завершение недели 2
        await send_photo_safe(
            callback,
            config.PHOTOS[8],
            content.WEEK_2_CONCLUSION,
            photo_num=8
        )
        if db.add_achievement(user_id, "week_2"):
            await callback.message.answer(content.get_achievement_message("week_2"))
        if db.add_achievement(user_id, "tasty"):
            await callback.message.answer(content.get_achievement_message("tasty"))
        await callback.message.answer(
            "Готова к финальной неделе?",
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 15:
        await callback.message.answer(
            content.DAY_15_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 17:
        await callback.message.answer(
            content.DAY_17_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
        # Ачивка "Максимальный тонус"
        if db.get_completed_glutes_count(user_id) >= 3:
            if db.add_achievement(user_id, "max_tone"):
                await callback.message.answer(content.get_achievement_message("max_tone"))
    elif day == 19:
        await callback.message.answer(
            content.DAY_19_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
        # Ачивка "Табата Queen"
        if db.get_completed_tabata_count(user_id) >= 4:
            if db.add_achievement(user_id, "tabata_queen"):
                await callback.message.answer(content.get_achievement_message("tabata_queen"))
    elif day == 21:
        await callback.message.answer(
            content.DAY_21_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    else:
        await callback.message.answer(
            f"День {day} выполнен! 🎉",
            reply_markup=keyboards.get_next_day_keyboard(day)
        )


@router.callback_query(F.data.startswith("completed_task_"))
async def completed_task(callback: CallbackQuery):
    """Обработка выполнения задания"""
    await callback.answer("✍️ Отлично! Задание зафиксировано")
    
    user_id = callback.from_user.id
    day = int(callback.data.split("_")[-1])
    
    # Отмечаем выполнение
    db.mark_day_completed(user_id, day, 'task')
    
    # Проверяем ачивки
    await check_and_give_achievements(callback.message, user_id, day)
    
    # Отправляем сообщение после выполнения задания
    if day == 2:
        await callback.message.answer(
            content.DAY_2_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 4:
        await callback.message.answer(
            content.DAY_4_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 6:
        await callback.message.answer(
            content.DAY_6_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 9:
        await callback.message.answer(
            content.DAY_9_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 11:
        await callback.message.answer(content.DAY_11_SNACK_IDEAS)
        await callback.message.answer(
            content.DAY_11_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 13:
        await callback.message.answer(
            content.DAY_13_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 16:
        await callback.message.answer(
            content.DAY_16_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 18:
        await callback.message.answer(
            content.DAY_18_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    elif day == 20:
        await callback.message.answer(
            content.DAY_20_COMPLETED,
            reply_markup=keyboards.get_next_day_keyboard(day)
        )
    else:
        await callback.message.answer(
            f"День {day} выполнен! 🎉",
            reply_markup=keyboards.get_next_day_keyboard(day)
        )


@router.callback_query(F.data.startswith("skip_day_"))
async def skip_day(callback: CallbackQuery):
    """Пропуск дня"""
    await callback.answer("День пропущен")
    day = int(callback.data.split("_")[-1])
    
    await callback.message.answer(
        "Ничего страшного, можно пропустить 💚\n"
        "Главное - не сдавайся и продолжай двигаться вперед!",
        reply_markup=keyboards.get_next_day_keyboard(day)
    )


# Обработчики для каждого дня

@router.callback_query(F.data == "start_day_2")
async def start_day_2(callback: CallbackQuery):
    """День 2 - Музыкальное задание"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(
        content.DAY_2_TEXT,
        reply_markup=keyboards.get_task_keyboard(2)
    )
    db.update_user_day(user_id, 2)


@router.callback_query(F.data == "start_day_3")
async def start_day_3(callback: CallbackQuery):
    """День 3 - Руки + Пресс"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_3_TEXT)
    await send_video_from_channel(callback.message, 3)
    await callback.message.answer(
        "📹 День 3 - Руки и Пресс",
        reply_markup=keyboards.get_workout_keyboard(3)
    )
    db.update_user_day(user_id, 3)


@router.callback_query(F.data == "start_day_4")
async def start_day_4(callback: CallbackQuery):
    """День 4 - 3 источника вдохновения"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await send_photo_safe(
        callback,
        config.PHOTOS[12],
        content.DAY_4_TEXT,
        reply_markup=keyboards.get_task_keyboard(4),
        photo_num=12
    )
    db.update_user_day(user_id, 4)


@router.callback_query(F.data == "start_day_5")
async def start_day_5(callback: CallbackQuery):
    """День 5 - Ягодицы"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_5_TEXT)
    await send_video_from_channel(callback.message, 5)
    await callback.message.answer(
        "📹 День 5 - Ягодицы",
        reply_markup=keyboards.get_workout_keyboard(5)
    )
    db.update_user_day(user_id, 5)


@router.callback_query(F.data == "start_day_6")
async def start_day_6(callback: CallbackQuery):
    """День 6 - Продуктовая корзина"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(
        content.DAY_6_TEXT,
        reply_markup=keyboards.get_task_keyboard(6)
    )
    db.update_user_day(user_id, 6)


@router.callback_query(F.data == "start_day_7")
async def start_day_7(callback: CallbackQuery):
    """День 7 - Танцевальная + Йога"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_7_TEXT)
    await send_video_from_channel(callback.message, "7_dance")
    await send_video_from_channel(callback.message, "7_yoga")
    await callback.message.answer(
        "📹 День 7 - Танцы + Йога",
        reply_markup=keyboards.get_workout_keyboard(7)
    )
    db.update_user_day(user_id, 7)


@router.callback_query(F.data == "start_day_8")
async def start_day_8(callback: CallbackQuery):
    """День 8 - НЕДЕЛЯ 2"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Отправляем контент недели 2
    await send_photo_safe(
        callback,
        config.PHOTOS[5],
        content.WEEK_2_START,
        reply_markup=keyboards.get_week_start_keyboard(2),
        photo_num=5
    )
    
    # Отправляем день 8
    await callback.message.answer(content.DAY_8_TEXT)
    await send_video_from_channel(callback.message, 8)
    await callback.message.answer(
        "📹 День 8 - Руки и Пресс с резинкой",
        reply_markup=keyboards.get_workout_keyboard(8)
    )
    db.update_user_day(user_id, 8)


@router.callback_query(F.data == "start_day_9")
async def start_day_9(callback: CallbackQuery):
    """День 9 - История о питании"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await send_photo_safe(
        callback,
        config.PHOTOS[10],
        content.DAY_9_TEXT,
        reply_markup=keyboards.get_task_keyboard(9),
        photo_num=10
    )
    db.update_user_day(user_id, 9)


@router.callback_query(F.data == "start_day_10")
async def start_day_10(callback: CallbackQuery):
    """День 10 - Ягодицы с резинкой"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_10_TEXT)
    await send_video_from_channel(callback.message, 10)
    await callback.message.answer(
        "📹 День 10 - Ягодицы с резинкой",
        reply_markup=keyboards.get_workout_keyboard(10)
    )
    db.update_user_day(user_id, 10)


@router.callback_query(F.data == "start_day_11")
async def start_day_11(callback: CallbackQuery):
    """День 11 - Осознанные перекусы"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(
        content.DAY_11_TEXT,
        reply_markup=keyboards.get_task_keyboard(11)
    )
    db.update_user_day(user_id, 11)


@router.callback_query(F.data == "start_day_12")
async def start_day_12(callback: CallbackQuery):
    """День 12 - Табата"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_12_TEXT)
    await send_video_from_channel(callback.message, 12)
    await callback.message.answer(
        "📹 День 12 - Табата",
        reply_markup=keyboards.get_workout_keyboard(12)
    )
    db.update_user_day(user_id, 12)


@router.callback_query(F.data == "start_day_13")
async def start_day_13(callback: CallbackQuery):
    """День 13 - Готовлю с любовью"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(
        content.DAY_13_TEXT,
        reply_markup=keyboards.get_task_keyboard(13)
    )
    db.update_user_day(user_id, 13)


@router.callback_query(F.data == "start_day_14")
async def start_day_14(callback: CallbackQuery):
    """День 14 - Танцы + Йога"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_14_TEXT)
    await send_video_from_channel(callback.message, 14)
    await send_video_from_channel(callback.message, "14_yoga")
    await callback.message.answer(
        "📹 День 14 - Танцы + Йога",
        reply_markup=keyboards.get_workout_keyboard(14)
    )
    db.update_user_day(user_id, 14)


@router.callback_query(F.data == "start_day_15")
async def start_day_15(callback: CallbackQuery):
    """День 15 - НЕДЕЛЯ 3"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Отправляем фото недели 3 с коротким заголовком
    week3_header = """✨ НЕДЕЛЯ 3 — #ПОЛНОЕПОГРУЖЕНИЕ

Финальный этап интенсива и, пожалуй, самый особенный 💫 За эти две недели ты уже укрепила тело, наладила питание и почувствовала уверенность. А теперь пришло время погрузиться полностью — в движение, привычку, лёгкость."""
    
    await send_photo_safe(
        callback,
        config.PHOTOS[6],
        week3_header,
        photo_num=6
    )
    
    # Отправляем остальной текст отдельно (из-за лимита caption 1024 символа)
    week3_details = """🎁 В честь завершения интенсива я дарю тебе доступ к 7-дневному пробному календарю тренировок Делай Тело (PDF ниже). Это тот самый формат, по которому занимаются девчонки из нашего фитнес-семейства с ежемесячной регулярностью:
- короткие экспресс-тренировки по 20–25 минут,
- разные форматы — от тонуса до растяжки,
- полная система ссылок на YouTube-видео прямо внутри файла.

💪 На этой неделе твоя цель:
● выполнять по одной тренировке календаря в дни отдыха, если чувствуешь силы;
● или даже добавить день из календаря к основным тренировкам интенсива, если чувствуешь, что сегодня можешь идти на все 200%.

📎 PDF с календарём прикреплён ниже. Дни в календаре уже упорядочены так, чтобы они шли в гармонии с соответствующими днями интенсива. Открой файл через Google Drive или Foxit PDF Reader, чтобы ссылки на тренировки были кликабельными.

Это твой мини-челлендж, чтобы проверить, как можно встроить регулярные занятия в повседневность легко и без перегрузки.

💫 Главное правило: слушай тело. Никаких "надо", только "хочу".

Пусть эта неделя станет твоим переходом к новому уровню системности, где движение становится естественной частью твоей жизни."""
    
    await callback.message.answer(week3_details)
    
    # Отправляем демо календарь
    await callback.message.answer(
        "📅 Получить демо-календарь:",
        reply_markup=keyboards.get_demo_calendar_keyboard()
    )
    db.update_user_day(user_id, 15)


@router.callback_query(F.data == "get_demo_calendar")
async def get_demo_calendar(callback: CallbackQuery):
    """Отправка демо календаря"""
    await callback.answer("Отправляю демо-календарь...")
    
    demo_calendar = FSInputFile(config.PDFS["demo_calendar"])
    await callback.message.answer_document(
        document=demo_calendar,
        caption="📅 ДемоКалендарь Интенсив"
    )
    
    # Отправляем день 15
    await callback.message.answer(content.DAY_15_TEXT)
    await send_video_from_channel(callback.message, 15)
    await callback.message.answer(
        "📹 День 15 - Руки и Пресс",
        reply_markup=keyboards.get_workout_keyboard(15)
    )


@router.callback_query(F.data == "start_day_16")
async def start_day_16(callback: CallbackQuery):
    """День 16 - 3 активности"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(
        content.DAY_16_TEXT,
        reply_markup=keyboards.get_task_keyboard(16)
    )
    db.update_user_day(user_id, 16)


@router.callback_query(F.data == "start_day_17")
async def start_day_17(callback: CallbackQuery):
    """День 17 - Ягодицы финал"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_17_TEXT)
    await send_video_from_channel(callback.message, 17)
    await callback.message.answer(
        "📹 День 17 - Ягодицы",
        reply_markup=keyboards.get_workout_keyboard(17)
    )
    db.update_user_day(user_id, 17)


@router.callback_query(F.data == "start_day_18")
async def start_day_18(callback: CallbackQuery):
    """День 18 - Твоя история"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(
        content.DAY_18_TEXT,
        reply_markup=keyboards.get_task_keyboard(18)
    )
    db.update_user_day(user_id, 18)


@router.callback_query(F.data == "start_day_19")
async def start_day_19(callback: CallbackQuery):
    """День 19 - Табата финал"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_19_TEXT)
    await send_video_from_channel(callback.message, 19)
    await callback.message.answer(
        "📹 День 19 - Табата",
        reply_markup=keyboards.get_workout_keyboard(19)
    )
    db.update_user_day(user_id, 19)


@router.callback_query(F.data == "start_day_20")
async def start_day_20(callback: CallbackQuery):
    """День 20 - Идеальный ритм"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await send_photo_safe(
        callback,
        config.PHOTOS[11],
        content.DAY_20_TEXT,
        reply_markup=keyboards.get_task_keyboard(20),
        photo_num=11
    )
    db.update_user_day(user_id, 20)


@router.callback_query(F.data == "start_day_21")
async def start_day_21(callback: CallbackQuery):
    """День 21 - Финальная тренировка"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await callback.message.answer(content.DAY_21_TEXT)
    await callback.message.answer(
        "🎥 Видео День 21 - Танцы (Bruno Mars + Shakira)\n(Видео будет отправлено из канала)",
        reply_markup=keyboards.get_workout_keyboard(21)
    )
    db.update_user_day(user_id, 21)


@router.callback_query(F.data == "start_day_22")
async def start_day_22(callback: CallbackQuery):
    """День 22 - Финал и подведение итогов"""
    await callback.answer()
    user_id = callback.from_user.id
    
    await send_photo_safe(
        callback,
        config.PHOTOS[9],
        content.DAY_22_TEXT,
        reply_markup=keyboards.get_upload_photo_keyboard("after"),
        photo_num=9
    )
    db.update_user_day(user_id, 22)


@router.callback_query(F.data == "upload_photo_after")
async def upload_photo_after(callback: CallbackQuery, state: FSMContext):
    """Запрос фото После"""
    await callback.answer("Загрузи фото «После»")
    await callback.message.answer("📸 Отправь фото «После» прямо сейчас:")
    await state.set_state(PhotoStates.waiting_for_photo_after)


@router.message(PhotoStates.waiting_for_photo_after, F.photo)
async def process_photo_after(message: Message, state: FSMContext):
    """Обработка фото После"""
    user_id = message.from_user.id
    
    # Получаем file_id
    photo = message.photo[-1]
    file_id = photo.file_id
    
    # Сохраняем в БД
    db.add_photo(user_id, 'after', file_id)
    
    await message.answer("✅ Фото «После» сохранено!")
    
    # Проверяем 100% выполнение
    if db.check_100_percent_completion(user_id):
        # 100% выполнено!
        if db.add_achievement(user_id, "100_percent"):
            await message.answer(content.get_achievement_message("100_percent"))
        
        await message.answer(
            content.DAY_22_SUCCESS,
            reply_markup=keyboards.get_certificate_keyboard()
        )
    else:
        await message.answer(
            "Почти готово! Для получения сертификата нужно выполнить все тренировки и задания 💪"
        )
    
    await state.clear()


@router.callback_query(F.data == "get_certificate")
async def get_certificate_handler(callback: CallbackQuery, state: FSMContext):
    """Генерация сертификата"""
    await callback.answer("Генерирую сертификат...")
    user_id = callback.from_user.id
    
    # Проверяем наличие имени в БД
    full_name = db.get_certificate_name(user_id)
    
    if not full_name:
        # Если имени нет, запрашиваем
        await callback.message.answer(
            "✍️ Напиши своё Имя и Фамилию так, как бы ты хотела, "
            "чтобы они отображались в сертификате:"
        )
        db.set_awaiting_name_input(user_id, True)
        return
    
    # Генерируем сертификат
    try:
        cert_path = generate_certificate(full_name, user_id)
        
        # Отправляем сертификат
        certificate = FSInputFile(cert_path)
        await callback.message.answer_document(
            document=certificate,
            caption=f"🎓 Сертификат для {full_name}"
        )
        
        # Отправляем промокод
        await callback.message.answer(
            f"🎁 ПРОМОКОД: {config.PROMO_CODE}\n\n"
            f"{config.PROMO_DESCRIPTION}\n\n"
            f"{content.DAY_22_FINAL_MESSAGE}"
        )
        
        # Отправляем фото ДО и ПОСЛЕ
        await send_before_after_photos(callback, user_id)
        
    except Exception as e:
        await callback.message.answer(f"Ошибка при генерации сертификата: {e}")


@router.message(F.text)
async def handle_certificate_name_input(message: Message):
    """Обработка ввода имени для сертификата в День 22"""
    user_id = message.from_user.id
    
    # Проверяем, ожидает ли бот ввода имени
    if db.is_awaiting_name_input(user_id):
        full_name = message.text.strip()
        
        # Разбираем имя и фамилию
        parts = full_name.split(maxsplit=1)
        first_name = parts[0] if len(parts) > 0 else full_name
        last_name = parts[1] if len(parts) > 1 else None
        
        # Сохраняем в БД
        db.set_certificate_name(user_id, first_name, last_name)
        db.set_awaiting_name_input(user_id, False)
        
        # Генерируем сертификат
        try:
            cert_path = generate_certificate(full_name, user_id)
            
            # Отправляем сертификат
            certificate = FSInputFile(cert_path)
            await message.answer_document(
                document=certificate,
                caption=f"🎓 Сертификат для {full_name}"
            )
            
            # Отправляем промокод
            await message.answer(
                f"🎁 ПРОМОКОД: {config.PROMO_CODE}\n\n"
                f"{config.PROMO_DESCRIPTION}\n\n"
                f"{content.DAY_22_FINAL_MESSAGE}"
            )
            
            # Отправляем фото ДО и ПОСЛЕ
            await send_before_after_photos(message, user_id)
            
        except Exception as e:
            await message.answer(f"Ошибка при генерации сертификата: {e}")


async def check_and_give_achievements(message: Message, user_id: int, day: int):
    """Проверка и выдача достижений"""
    progress = db.get_user_progress(user_id)
    
    # Проверка "Полпути" (50%)
    if progress['percentage'] >= 50:
        if db.add_achievement(user_id, "halfway"):
            await message.answer(content.get_achievement_message("halfway"))
    
    # Проверка недельных ачивок
    if day == 7:
        if db.add_achievement(user_id, "alone"):
            await message.answer(content.get_achievement_message("alone"))
    
    if day == 14:
        if db.add_achievement(user_id, "tasty"):
            await message.answer(content.get_achievement_message("tasty"))
    
    if day == 15:
        if db.add_achievement(user_id, "immersion"):
            await message.answer(content.get_achievement_message("immersion"))

