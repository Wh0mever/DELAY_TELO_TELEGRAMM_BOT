# -*- coding: utf-8 -*-
"""
Обработчики меню бота
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from database import db
import content
import keyboards

router = Router()


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    """Главное меню"""
    await callback.answer()
    await callback.message.answer(
        "📋 Главное меню Табата-Интенсив:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )


@router.callback_query(F.data == "my_progress")
async def my_progress(callback: CallbackQuery):
    """Мой прогресс"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Получаем прогресс
    progress = db.get_user_progress(user_id)
    user = db.get_user(user_id)
    achievements = db.get_user_achievements(user_id)
    
    # Формируем сообщение
    message_text = f"""📊 **Твой прогресс в интенсиве**

🗓 Текущий день: {user['current_day']}

💪 Тренировок выполнено: {progress['workouts']}
✍️ Заданий выполнено: {progress['tasks']}
⭐ Всего баллов: {progress['points']}
📈 Прогресс: {progress['percentage']}%

🏆 **Достижения:**
"""
    
    if achievements:
        for ach in achievements:
            ach_name = content.ACHIEVEMENTS.get(ach['achievement_name'], ach['achievement_name'])
            message_text += f"• {ach_name}\n"
    else:
        message_text += "Пока нет достижений. Продолжай тренироваться!\n"
    
    await callback.message.answer(
        message_text,
        parse_mode="Markdown",
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )


@router.callback_query(F.data == "schedule")
async def schedule(callback: CallbackQuery):
    """Расписание интенсива"""
    await callback.answer()
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    current_day = user['current_day']
    
    schedule_text = f"""📅 <b>РАСПИСАНИЕ ИНТЕНСИВА</b>

<b>НЕДЕЛЯ 1 – #НАЕДИНЕССОБОЙ</b>
День 1 — Музыкальная Табата
День 2 — Музыкальное задание
День 3 — Руки + Пресс
День 4 — 3 источника вдохновения
День 5 — Ягодицы
День 6 — Продуктовая корзина
День 7 — Танцевальная + Йога

<b>НЕДЕЛЯ 2 – #МЕНЯЮСЬВКУСНО</b>
День 8 — Руки + Пресс (с резинкой)
День 9 — История о питании
День 10 — Ягодицы (с резинкой)
День 11 — Осознанные перекусы
День 12 — Музыкальная Табата
День 13 — Готовлю с любовью
День 14 — Танцы + Йога

<b>НЕДЕЛЯ 3 – #ПОЛНОЕПОГРУЖЕНИЕ</b>
День 15 — Руки + Пресс (с резинкой)
День 16 — 3 активности
День 17 — Ягодицы (финал)
День 18 — Твоя история
День 19 — Табата (финал)
День 20 — Идеальный ритм
День 21 — Финальная тренировка
День 22 — Подведение итогов

Ты сейчас на дне: <b>{current_day}</b>
"""
    
    await callback.message.answer(
        schedule_text,
        parse_mode="HTML",
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )


@router.callback_query(F.data == "help")
async def help_menu(callback: CallbackQuery):
    """Помощь"""
    await callback.answer()
    
    help_text = """❓ **ПОМОЩЬ**

**Как работает интенсив?**
Каждый день открывается новая тренировка или задание. Выполняй их и нажимай кнопки «✅ ВЫПОЛНИЛА» или «✍️ СДЕЛАНО».

**Что такое достижения?**
За выполнение определенных условий (неделя без пропусков, все табаты и т.д.) ты получаешь специальные ачивки.

**Как получить сертификат?**
Выполни все тренировки и задания, загрузи фото ДО и ПОСЛЕ, и сертификат будет автоматически сгенерирован на День 22.

**Что делать если пропустила день?**
Ничего страшного! Можешь нажать кнопку «❌ ПРОПУСКАЮ» и перейти к следующему дню. Но помни, что для получения сертификата нужно выполнить все дни.

**Команды бота:**
/start - начать сначала
/menu - главное меню
/profile - мой профиль
/photo - моё фото ДО

**Поддержка:**
По всем вопросам пиши @delaytelofit
"""
    
    await callback.message.answer(
        help_text,
        parse_mode="Markdown",
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )


@router.callback_query(F.data == "my_profile")
async def my_profile(callback: CallbackQuery):
    """Мой профиль"""
    await callback.answer()
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await callback.message.answer("❌ Пользователь не найден. Нажмите /start")
        return
    
    # Формируем информацию о профиле
    profile_text = f"""👤 <b>МОЙ ПРОФИЛЬ</b>

<b>Имя:</b> {user['first_name']}
"""
    
    # Добавляем фамилию если есть
    if user['last_name']:
        profile_text += f"<b>Фамилия:</b> {user['last_name']}\n"
    
    # Добавляем username если есть
    if user['username']:
        profile_text += f"<b>Username:</b> @{user['username']}\n"
    
    profile_text += f"""
<b>📅 Дата регистрации:</b> {user['registration_date'][:10]}
<b>📍 Текущий день:</b> День {user['current_day']}

<b>📊 Статистика:</b>
• Всего дней пройдено: {db.get_user_total_score(user_id)}
• Текущий прогресс: {int((db.get_user_total_score(user_id) / 22) * 100)}%
"""
    
    # Добавляем достижения
    achievements = db.get_user_achievements(user_id)
    if achievements:
        profile_text += f"\n<b>🏆 Достижения:</b> {len(achievements)}\n"
        for ach in achievements:
            emoji = content.get_achievement_emoji(ach['achievement_name'])
            profile_text += f"{emoji} "
    
    await callback.message.answer(
        profile_text,
        parse_mode="HTML",
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )


@router.callback_query(F.data == "my_photo_before")
async def my_photo_before(callback: CallbackQuery):
    """Показать фото ДО"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Получаем фото ДО из базы
    photo = db.get_photo(user_id, "before")
    
    if not photo:
        await callback.message.answer(
            "📸 У вас пока нет фото ДО.\n\n"
            "Фото ДО загружается при старте интенсива (День 0).",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
        return
    
    # Отправляем фото
    try:
        await callback.message.answer_photo(
            photo=photo['file_id'],
            caption=f"📸 <b>Твоё фото ДО</b>\n\n"
                    f"Загружено: {photo['uploaded_at'][:10]}\n\n"
                    f"💪 Продолжай работать над собой!\n"
                    f"Уже скоро увидишь разницу!",
            parse_mode="HTML",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await callback.message.answer(
            f"⚠️ Не удалось загрузить фото.\n\n"
            f"Попробуйте позже или обратитесь в поддержку @delaytelofit",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
        print(f"Ошибка отправки фото ДО: {e}")


# Команды для прямого доступа к функциям
@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Команда /menu - главное меню"""
    await message.answer(
        "📋 Главное меню Табата-Интенсив:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Команда /profile - мой профиль"""
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        await message.answer("❌ Пользователь не найден. Нажмите /start")
        return
    
    # Формируем информацию о профиле
    profile_text = f"""👤 <b>МОЙ ПРОФИЛЬ</b>

<b>Имя:</b> {user['first_name']}
"""
    
    # Добавляем фамилию если есть
    if user['last_name']:
        profile_text += f"<b>Фамилия:</b> {user['last_name']}\n"
    
    # Добавляем username если есть
    if user['username']:
        profile_text += f"<b>Username:</b> @{user['username']}\n"
    
    profile_text += f"""
<b>📅 Дата регистрации:</b> {user['registration_date'][:10]}
<b>📍 Текущий день:</b> День {user['current_day']}

<b>📊 Статистика:</b>
• Всего дней пройдено: {db.get_user_total_score(user_id)}
• Текущий прогресс: {int((db.get_user_total_score(user_id) / 22) * 100)}%
"""
    
    # Добавляем достижения
    achievements = db.get_user_achievements(user_id)
    if achievements:
        profile_text += f"\n<b>🏆 Достижения:</b> {len(achievements)}\n"
        for ach in achievements:
            emoji = content.get_achievement_emoji(ach['achievement_name'])
            profile_text += f"{emoji} "
    
    await message.answer(
        profile_text,
        parse_mode="HTML",
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )


@router.message(Command("photo"))
async def cmd_photo(message: Message):
    """Команда /photo - моё фото ДО"""
    user_id = message.from_user.id
    
    # Получаем фото ДО из базы
    photo = db.get_photo(user_id, "before")
    
    if not photo:
        await message.answer(
            "📸 У вас пока нет фото ДО.\n\n"
            "Фото ДО загружается при старте интенсива (День 0).",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
        return
    
    # Отправляем фото
    try:
        await message.answer_photo(
            photo=photo['file_id'],
            caption=f"📸 <b>Твоё фото ДО</b>\n\n"
                    f"Загружено: {photo['uploaded_at'][:10]}\n\n"
                    f"💪 Продолжай работать над собой!\n"
                    f"Уже скоро увидишь разницу!",
            parse_mode="HTML",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"⚠️ Не удалось загрузить фото.\n\n"
            f"Попробуйте позже или обратитесь в поддержку @delaytelofit",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
        print(f"Ошибка отправки фото ДО: {e}")

