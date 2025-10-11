# -*- coding: utf-8 -*-
"""
Обработчик старта и регистрации
"""

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import content
import keyboards
from database import db

router = Router()


class RegistrationStates(StatesGroup):
    """Состояния регистрации"""
    waiting_for_name = State()
    waiting_for_photo_before = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Проверяем, существует ли пользователь
    if db.user_exists(user_id):
        # Пользователь уже зарегистрирован
        user = db.get_user(user_id)
        await message.answer(
            f"С возвращением, {first_name}! 👋\n\n"
            f"Ты на {user['current_day']} дне интенсива.\n\n"
            f"Используй /menu для доступа к функциям бота.",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
    else:
        # Новый пользователь - регистрируем
        db.add_user(user_id, username, first_name, last_name)
        
        # Отправляем День 0 - Приветствие с Фото 1
        # Импортируем send_photo_safe из days
        from handlers.days import send_photo_safe
        await send_photo_safe(
            message,
            config.PHOTOS[1],
            content.DAY_0_WELCOME,
            reply_markup=keyboards.get_start_keyboard(),
            photo_num=1  # Указываем номер фото для отправки из канала
        )


@router.callback_query(F.data == "how_it_works")
async def how_it_works(callback: CallbackQuery):
    """Как всё устроено"""
    await callback.answer()
    
    # Отправляем Фото 2
    from handlers.days import send_photo_safe
    await send_photo_safe(
        callback,
        config.PHOTOS[2],
        content.DAY_0_HOW_IT_WORKS,
        reply_markup=keyboards.get_steps_keyboard(),
        photo_num=2
    )


@router.callback_query(F.data == "first_steps")
async def first_steps(callback: CallbackQuery):
    """Первые простые шаги"""
    await callback.answer()
    
    # Отправляем Фото 3
    from handlers.days import send_photo_safe
    await send_photo_safe(
        callback,
        config.PHOTOS[3],
        content.DAY_0_FIRST_STEPS,
        photo_num=3
    )
    
    # Отправляем PDF файлы
    try:
        guide = FSInputFile(config.PDFS["guide"])
        await callback.message.answer_document(
            document=guide,
            caption="📕 Гайд Интенсива ДелайТело"
        )
    except Exception as e:
        print(f"⚠️ Ошибка отправки Гайда: {e}")
    
    try:
        trackers = FSInputFile(config.PDFS["trackers"])
        await callback.message.answer_document(
            document=trackers,
            caption="📋 Трекеры Чат Реалити"
        )
    except Exception as e:
        print(f"⚠️ Ошибка отправки Трекеров: {e}")
    
    # Кнопка "Готова начать" в любом случае
    await callback.message.answer(
        "Нажми кнопку ниже, когда будешь готова начать! 👇",
        reply_markup=keyboards.get_ready_keyboard()
    )


@router.callback_query(F.data == "ready_to_start")
async def ready_to_start(callback: CallbackQuery, state: FSMContext):
    """Готова начать - запрос имени"""
    await callback.answer("Отлично! Давай познакомимся 😊")
    
    user_id = callback.from_user.id
    
    # Выдаем достижение "Старт"
    if db.add_achievement(user_id, "start"):
        await callback.message.answer(content.get_achievement_message("start"))
    
    # Запрашиваем имя для сертификата
    await callback.message.answer(content.DAY_0_REQUEST_NAME)
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка ввода имени"""
    user_id = message.from_user.id
    full_name = message.text.strip()
    
    # Разбираем имя и фамилию
    parts = full_name.split(maxsplit=1)
    first_name = parts[0] if len(parts) > 0 else full_name
    last_name = parts[1] if len(parts) > 1 else None
    
    # Сохраняем в БД
    db.set_certificate_name(user_id, first_name, last_name)
    
    # Запрашиваем фото "До"
    await message.answer(content.DAY_0_REQUEST_PHOTO)
    await state.set_state(RegistrationStates.waiting_for_photo_before)


@router.message(RegistrationStates.waiting_for_photo_before, F.photo)
async def process_photo_before(message: Message, state: FSMContext):
    """Обработка фото До"""
    user_id = message.from_user.id
    
    # Получаем file_id самого большого фото
    photo = message.photo[-1]
    file_id = photo.file_id
    
    # Сохраняем в БД
    db.add_photo(user_id, 'before', file_id)
    
    # Отмечаем День 0 как выполненный
    db.mark_day_completed(user_id, 0, 'start')
    db.update_user_day(user_id, 0)
    
    await message.answer(
        "✅ Отлично! Фото «До» сохранено.\n\n"
        "Теперь ты готова начать интенсив! 🔥\n\n"
        "Завтра в 09:00 откроется День 1, но ты можешь начать прямо сейчас!",
        reply_markup=keyboards.get_week_start_keyboard(1)
    )
    
    await state.clear()


@router.message(Command("menu"))
async def show_menu(message: Message):
    """Показать главное меню"""
    await message.answer(
        "📋 Главное меню Табата-Интенсив:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )

