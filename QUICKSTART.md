# 🚀 Быстрый старт

## ⚡ За 5 минут до запуска

### Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 2: Проверка файлов

Убедитесь, что у вас есть:
- ✅ `Sertificate.png` - шаблон сертификата в корне
- ✅ Папка `Табата-Интенсив/` с фото и PDF
- ✅ Токен бота в `config.py` (уже настроен)

### Шаг 3: Запуск бота

```bash
python bot.py
```

**Готово!** Бот запущен и готов к работе 🎉

---

## 📹 Настройка видео (опционально)

Сейчас видео отправляются как текстовые заглушки. Чтобы отправлять реальные видео:

### Вариант 1: Быстрая настройка через скрипт

1. Создайте приватный канал в Telegram
2. Загрузите все видео в канал
3. Запустите скрипт настройки:

```bash
python setup_videos.py
```

4. Перешлите видео из канала скрипту
5. Скопируйте полученные file_id

### Вариант 2: Вручную

Смотрите подробную инструкцию в `VIDEO_SETUP.md`

---

## 🧪 Тестирование

### Проверка основных функций:

1. **Старт**: отправьте `/start` боту
2. **Регистрация**: введите имя и фамилию
3. **Фото До**: загрузите фото
4. **День 1**: нажмите кнопку перехода к Дню 1
5. **Выполнение**: нажмите "✅ ВЫПОЛНИЛА"
6. **Прогресс**: `/menu` → "Мой прогресс"

### Проверка финала (День 22):

Для быстрого тестирования можно вручную обновить день в БД:

```python
from database import db
db.update_user_day(USER_ID, 22)
```

---

## 📂 Структура проекта

```
Табата-Интенсив Бот/
│
├── 🤖 bot.py                   # Запуск бота
├── ⚙️ config.py                # Конфигурация
├── 💾 database.py              # SQLite база
├── 🎹 keyboards.py             # Клавиатуры
├── 📝 content.py               # Контент 22 дней
├── 🎓 certificate_generator.py # Сертификаты
├── ⏰ scheduler.py             # Напоминания
│
├── 📁 handlers/
│   ├── start.py               # Регистрация
│   ├── days.py                # Все 22 дня
│   ├── menu.py                # Меню
│   └── progress.py            # Прогресс
│
├── 📁 Табата-Интенсив/         # Медиа
├── 📁 certificates/            # Сертификаты
└── 📄 Sertificate.png          # Шаблон
```

---

## 🔑 Основные команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать интенсив |
| `/menu` | Главное меню |
| **Кнопки:** | |
| ✅ ВЫПОЛНИЛА | Отметить тренировку |
| ✍️ СДЕЛАНО | Отметить задание |
| ❌ ПРОПУСКАЮ | Пропустить день |

---

## 🏆 Достижения

- 🔥 Мощный Старт
- ⚡ Первая неделя
- 💪 Полпути (50%)
- 🎧 Наедине с собой
- 🍽 Меняюсь вкусно
- 🌊 Погружение
- 👑 Табата Queen
- 💪 Максимальный Тонус
- 🎉 100% (с сертификатом!)

---

## 🐛 Решение проблем

### Бот не запускается

```bash
# Проверьте установку
pip list | grep aiogram
pip list | grep pillow
pip list | grep apscheduler

# Переустановите при необходимости
pip install --upgrade -r requirements.txt
```

### Ошибка с файлами

```python
# Проверьте пути в config.py
import config
print(config.PHOTOS[1])  # Должен существовать
print(config.CERTIFICATE_TEMPLATE)  # Должен существовать
```

### Ошибка базы данных

```bash
# Удалите и пересоздайте БД
rm tabata_bot.db
python bot.py  # БД создастся автоматически
```

### Проблемы с кодировкой (Windows)

Если видите кракозябры вместо русского текста:

```bash
# Запустите с указанием кодировки
chcp 65001
python bot.py
```

---

## 📊 Мониторинг

### Просмотр логов

Логи выводятся в консоль. Для сохранения в файл:

```bash
python bot.py > bot.log 2>&1
```

### Проверка БД

```python
from database import db

# Посмотреть всех пользователей
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(dict(user))
conn.close()
```

---

## 🚀 Деплой на сервер

### На VPS (Ubuntu/Debian):

```bash
# 1. Установите Python 3.9+
sudo apt update
sudo apt install python3 python3-pip

# 2. Клонируйте проект
git clone YOUR_REPO
cd tabata-bot

# 3. Установите зависимости
pip3 install -r requirements.txt

# 4. Запустите в фоне
nohup python3 bot.py &

# Или используйте systemd/supervisor для автозапуска
```

### Systemd сервис:

Создайте `/etc/systemd/system/tabata-bot.service`:

```ini
[Unit]
Description=Tabata Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Запустите:
```bash
sudo systemctl enable tabata-bot
sudo systemctl start tabata-bot
sudo systemctl status tabata-bot
```

---

## 💡 Полезные ссылки

- 📖 Полная документация: `README.md`
- 🎬 Настройка видео: `VIDEO_SETUP.md`
- 📋 ТЗ интенсива: `Tex_Zadanie.txt`

---

## ✅ Чеклист перед запуском

- [ ] Установлены все зависимости (`pip install -r requirements.txt`)
- [ ] Токен бота в `config.py`
- [ ] Файл `Sertificate.png` в корне
- [ ] Папка `Табата-Интенсив/` с медиа
- [ ] Бот запускается без ошибок (`python bot.py`)
- [ ] Отправили `/start` и прошли регистрацию
- [ ] (Опционально) Настроены file_id для видео

---

**Готово! Теперь ваш бот работает! 🎉**

Для вопросов: @delaytelofit

