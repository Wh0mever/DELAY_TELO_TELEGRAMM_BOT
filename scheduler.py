# -*- coding: utf-8 -*-
"""
Планировщик задач для автоматического открытия дней
"""

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
import keyboards
from database import db


async def send_daily_reminder(bot: Bot):
    """Отправка ежедневных напоминаний в 09:00"""
    # Получаем всех пользователей
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, current_day FROM users WHERE current_day < 22')
    users = cursor.fetchall()
    conn.close()
    
    for user in users:
        user_id = user['user_id']
        current_day = user['current_day']
        next_day = current_day + 1
        
        # Проверяем, выполнен ли текущий день
        # (можно добавить более сложную логику)
        
        try:
            await bot.send_message(
                user_id,
                f"🌅 Доброе утро! \n\n"
                f"Сегодня тебя ждёт День {next_day} интенсива! 🔥\n\n"
                f"Готова к новым свершениям?",
                reply_markup=keyboards.get_next_day_keyboard(current_day)
            )
        except Exception as e:
            print(f"Ошибка отправки напоминания пользователю {user_id}: {e}")


def setup_scheduler(bot: Bot):
    """Настройка планировщика"""
    scheduler = AsyncIOScheduler()
    
    # Добавляем задачу на отправку напоминаний каждый день в 09:00
    scheduler.add_job(
        send_daily_reminder,
        'cron',
        hour=9,
        minute=0,
        args=[bot]
    )
    
    return scheduler

