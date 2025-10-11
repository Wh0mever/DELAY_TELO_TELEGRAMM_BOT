# -*- coding: utf-8 -*-
"""
Главный файл Telegram-бота Табата-Интенсив
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers import start, days, menu, progress
from scheduler import setup_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(days.router)
    dp.include_router(menu.router)
    dp.include_router(progress.router)
    
    # Настройка планировщика
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    logger.info("Бот запущен!")
    
    try:
        # Запуск polling
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()
        scheduler.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")

