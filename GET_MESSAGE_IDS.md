# Как получить правильные Message ID из канала

## Проблема
Бот настроен на пересылку видео из канала, но message_id могут не совпадать с порядком постов.

## Решение: Получение точных message_id

### Способ 1: Через @RawDataBot

1. Добавьте @RawDataBot в ваш канал как администратора
2. Перешлите каждое видео боту @RawDataBot
3. Он пришлет JSON с данными, найдите `"message_id": 123`
4. Обновите `config.py` с правильными ID

### Способ 2: Скрипт для получения message_id

Создайте `get_channel_messages.py`:

```python
import asyncio
from aiogram import Bot

BOT_TOKEN = "8357062293:AAFChKKrpKLIU_cSSTVF3QV4WeDk5Bf4nYg"
CHANNEL_ID = -1003006477133

async def get_messages():
    bot = Bot(token=BOT_TOKEN)
    
    print("Получение сообщений из канала...\n")
    print("="*60)
    
    # Перебираем message_id от 1 до 50
    for msg_id in range(1, 51):
        try:
            # Пытаемся переслать сообщение себе
            message = await bot.forward_message(
                chat_id=YOUR_USER_ID,  # Замените на ваш user_id
                from_chat_id=CHANNEL_ID,
                message_id=msg_id
            )
            
            # Получаем информацию о сообщении
            if message.video:
                caption = message.caption or "Без подписи"
                print(f"Message ID: {msg_id}")
                print(f"Тип: VIDEO")
                print(f"Подпись: {caption}")
                print("-" * 60)
        except Exception as e:
            # Сообщение не найдено или ошибка
            pass
    
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(get_messages())
```

### Способ 3: Вручную через Telegram Desktop

1. Откройте канал в Telegram Desktop
2. Нажмите правой кнопкой на сообщение → "Copy Message Link"
3. Ссылка будет вида: `https://t.me/c/3006477133/123`
4. Число после последнего "/" - это message_id (123)

## Обновление config.py

После получения правильных message_id, обновите `config.py`:

```python
VIDEO_MESSAGE_IDS = {
    1: ПРАВИЛЬНЫЙ_ID,      # День 1 - Табата
    3: ПРАВИЛЬНЫЙ_ID,      # День 3 - Руки и пресс
    5: ПРАВИЛЬНЫЙ_ID,      # День 5 - Ягодицы
    "7_yoga": ПРАВИЛЬНЫЙ_ID,     # День 7 - Йога
    "7_dance": ПРАВИЛЬНЫЙ_ID,    # День 7 - Танцы Бруно Марс
    8: ПРАВИЛЬНЫЙ_ID,      # День 8 - Руки и пресс
    10: ПРАВИЛЬНЫЙ_ID,     # День 10 - Ягодицы
    12: ПРАВИЛЬНЫЙ_ID,     # День 12 - Табата
    14: ПРАВИЛЬНЫЙ_ID,     # День 14 - Танцы
    15: ПРАВИЛЬНЫЙ_ID,     # День 15 - Руки и пресс
    17: ПРАВИЛЬНЫЙ_ID,     # День 17 - Ягодицы
    19: ПРАВИЛЬНЫЙ_ID,     # День 19 - Табата
    "14_yoga": ПРАВИЛЬНЫЙ_ID,   # День 14 - Йога
}
```

## Проверка

После обновления, отправьте боту `/start` и проверьте что видео приходят правильно.

Если видео не приходит, проверьте:
1. Бот добавлен в канал как администратор
2. Message ID правильный
3. Channel ID правильный (-1003006477133)

