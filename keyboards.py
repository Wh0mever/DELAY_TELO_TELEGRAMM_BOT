# -*- coding: utf-8 -*-
"""
Клавиатуры для бота
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard():
    """Клавиатура для начала (День 0)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="КАК ВСЁ УСТРОЕНО", callback_data="how_it_works")]
    ])
    return keyboard


def get_steps_keyboard():
    """Клавиатура для первых шагов"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ПЕРВЫЕ ПРОСТЫЕ ШАГИ 👇", callback_data="first_steps")]
    ])
    return keyboard


def get_ready_keyboard():
    """Клавиатура готовности начать"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ ГОТОВА НАЧАТЬ", callback_data="ready_to_start")]
    ])
    return keyboard


def get_week_start_keyboard(week: int):
    """Клавиатура для начала недели"""
    if week == 1:
        callback = "start_day_1"
        text = "🚀 ПЕРЕЙТИ К 1 ДНЮ"
    elif week == 2:
        callback = "start_day_8"
        text = "🚀 ПЕРЕЙТИ К ДНЮ 8"
    else:  # week 3
        callback = "start_day_15"
        text = "🚀 ДЕНЬ 15"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=callback)]
    ])
    return keyboard


def get_workout_keyboard(day: int, has_skip: bool = True):
    """Клавиатура для тренировочных дней"""
    buttons = [
        [InlineKeyboardButton(text="✅ ВЫПОЛНИЛА", callback_data=f"completed_workout_{day}")]
    ]
    if has_skip:
        buttons.append([InlineKeyboardButton(text="❌ ПРОПУСКАЮ", callback_data=f"skip_day_{day}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_task_keyboard(day: int, has_skip: bool = True):
    """Клавиатура для дней с заданиями"""
    buttons = [
        [InlineKeyboardButton(text="✍️ СДЕЛАНО", callback_data=f"completed_task_{day}")]
    ]
    if has_skip:
        buttons.append([InlineKeyboardButton(text="❌ ПРОПУСКАЮ", callback_data=f"skip_day_{day}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_next_day_keyboard(day: int):
    """Клавиатура для перехода к следующему дню"""
    day_names = {
        1: "🌿 ДЕНЬ 2",
        2: "💪 ДЕНЬ 3",
        3: "🌸 ДЕНЬ 4",
        4: "🍑 ДЕНЬ 5",
        5: "🥑 ДЕНЬ 6",
        6: "💃 ДЕНЬ 7",
        7: "✨ НЕДЕЛЯ 2",
        8: "🥑 ДЕНЬ 9",
        9: "🔥 ДЕНЬ 10",
        10: "🥨 ДЕНЬ 11",
        11: "🔥 ДЕНЬ 12",
        12: "🥗 ДЕНЬ 13",
        13: "🔥 ДЕНЬ 14",
        14: "✨ НЕДЕЛЯ 3",
        15: "✨ ДЕНЬ 16",
        16: "🔥 ДЕНЬ 17",
        17: "✨ ДЕНЬ 18",
        18: "💫 ДЕНЬ 19",
        19: "✨ ДЕНЬ 20",
        20: "💃 ДЕНЬ 21",
        21: "✨ ПОДВЕДЕНИЕ ИТОГОВ"
    }
    
    text = day_names.get(day, f"ДЕНЬ {day + 1}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"start_day_{day + 1}")]
    ])
    return keyboard


def get_demo_calendar_keyboard():
    """Клавиатура для получения демо календаря"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 ПОЛУЧИТЬ ДЕМО КАЛЕНДАРИК!", callback_data="get_demo_calendar")]
    ])
    return keyboard


def get_upload_photo_keyboard(photo_type: str):
    """Клавиатура для загрузки фото"""
    text = "📸 ЗАГРУЗИТЬ ФОТО 'ПОСЛЕ'" if photo_type == "after" else "📸 ЗАГРУЗИТЬ ФОТО 'ДО'"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"upload_photo_{photo_type}")]
    ])
    return keyboard


def get_certificate_keyboard():
    """Клавиатура для получения сертификата"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 ЗАБРАТЬ СЕРТИФИКАТ", callback_data="get_certificate")]
    ])
    return keyboard


def get_main_menu_keyboard():
    """Главное меню бота"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")],
        [InlineKeyboardButton(text="📊 Мой прогресс", callback_data="my_progress")],
        [InlineKeyboardButton(text="📸 Моё фото ДО", callback_data="my_photo_before")],
        [InlineKeyboardButton(text="📅 Расписание", callback_data="schedule")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])
    return keyboard


def get_back_to_menu_keyboard():
    """Кнопка возврата в меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="main_menu")]
    ])
    return keyboard

