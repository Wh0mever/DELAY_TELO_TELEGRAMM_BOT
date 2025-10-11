# 🚀 Загрузка проекта на GitHub

Пошаговая инструкция по загрузке бота на GitHub.

## Подготовка

### 1. Создайте репозиторий на GitHub

1. Перейдите на [github.com](https://github.com)
2. Нажмите "+" в правом верхнем углу → "New repository"
3. Заполните:
   - **Repository name**: `DELAY_TELO_TELEGRAMM_BOT` (или свое название)
   - **Description**: "Telegram bot для 21-дневного фитнес-интенсива"
   - **Public** или **Private** (по желанию)
   - ❌ НЕ ставьте галочку "Add README" (у нас уже есть)
4. Нажмите "Create repository"

### 2. Установите Git (если нет)

**Windows:**
- Скачайте с [git-scm.com](https://git-scm.com/download/win)
- Установите с настройками по умолчанию

**Linux:**
```bash
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL
```

**Mac:**
```bash
brew install git
```

## Загрузка проекта

### Вариант 1: Через командную строку

Откройте командную строку (cmd) или PowerShell в папке проекта:

```bash
# 1. Инициализируйте Git
git init

# 2. Добавьте все файлы
git add .

# 3. Сделайте первый commit
git commit -m "Initial commit: Telegram bot for fitness intensive"

# 4. Переименуйте ветку в main (если нужно)
git branch -M main

# 5. Добавьте remote (замените YOUR_USERNAME и REPO_NAME)
git remote add origin https://github.com/wh0mever/DELAY_TELO_TELEGRAMM_BOT.git

# 6. Загрузите на GitHub
git push -u origin main
```

### Вариант 2: Через GitHub Desktop

1. Скачайте [GitHub Desktop](https://desktop.github.com/)
2. Установите и войдите в аккаунт
3. File → Add Local Repository
4. Выберите папку проекта
5. Нажмите "Publish repository"

## Важно: Безопасность

### ⚠️ НЕ загружайте на GitHub:

- ❌ Токен бота (в `config.py`)
- ❌ База данных (`tabata_bot.db`)
- ❌ Сгенерированные сертификаты
- ❌ Личные данные пользователей

### ✅ Как защитить токен:

#### Вариант 1: Замените токен на placeholder

В `config.py`:
```python

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Получите токен у @BotFather
```

#### Вариант 2: Используйте `.env` файл

1. Создайте `.env` (уже в `.gitignore`):
```bash
BOT_TOKEN=*************************************************************
VIDEO_CHANNEL_ID=-1000000000000
```

2. Установите `python-dotenv`:
```bash
pip install python-dotenv
```

3. Измените `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
VIDEO_CHANNEL_ID = int(os.getenv('VIDEO_CHANNEL_ID'))
```

4. Добавьте пример `.env.example`:
```bash
BOT_TOKEN=your_token_here
VIDEO_CHANNEL_ID=your_channel_id_here
```

## Проверка перед загрузкой

### Убедитесь что `.gitignore` правильный:

```bash
# Проверьте, что эти файлы НЕ будут загружены:
git status

# Если видите tabata_bot.db или токен - добавьте в .gitignore!
```

### Проверьте, что загружается:

```bash
git ls-files
```

Должны быть:
- ✅ `bot.py`, `config.py` (без токена!), `database.py`
- ✅ `handlers/*.py`
- ✅ `README.md`, `requirements.txt`
- ✅ `.gitignore`, `LICENSE`
- ❌ `tabata_bot.db`
- ❌ `certificates/*.png` (кроме `.gitkeep`)

## Добавление скриншотов

1. Сделайте скриншоты бота
2. Сохраните в `.github/screenshots/`
3. Добавьте в Git:
```bash
git add .github/screenshots/*.png
git commit -m "docs: добавлены скриншоты бота"
git push
```

## Обновление репозитория

После изменений в коде:

```bash
# 1. Проверьте изменения
git status

# 2. Добавьте файлы
git add .

# 3. Commit с описанием
git commit -m "feat: добавлена новая функция"

# 4. Загрузите на GitHub
git push
```

## Полезные Git команды

```bash
# Посмотреть историю
git log --oneline

# Отменить последний commit (файлы останутся)
git reset --soft HEAD~1

# Посмотреть изменения
git diff

# Посмотреть ветки
git branch -a

# Создать новую ветку
git checkout -b feature/new-feature

# Вернуться на main
git checkout main

# Обновить с GitHub
git pull
```

## Настройка GitHub репозитория

### После загрузки:

1. **About** (справа сверху):
   - Description: "Telegram bot для 21-дневного фитнес-интенсива с геймификацией"
   - Website: ссылка на бота (если есть)
   - Topics: `telegram-bot`, `python`, `fitness`, `aiogram`, `sqlite`

2. **README.md**:
   - Добавьте скриншоты в `.github/screenshots/`
   - Обновите ссылки на свой username

3. **Settings**:
   - Features → Issues ✅ (для багов)
   - Features → Discussions ✅ (для вопросов)

## Статус репозитория

### Бейджи для README:

Добавьте в начало README.md:

```markdown
![Python Version](https://img.shields.io/badge/python-3.11+-blue)
![Bot Status](https://img.shields.io/badge/bot-active-green)
![License](https://img.shields.io/badge/license-MIT-green)
![GitHub Stars](https://img.shields.io/github/stars/YOUR_USERNAME/telegram-tabata-bot)
```

## Проблемы и решения

### Ошибка: "remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### Ошибка: "failed to push"

```bash
git pull origin main --rebase
git push origin main
```

### Случайно загрузили токен?

1. Немедленно смените токен у @BotFather
2. Удалите файл из истории Git:
```bash
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch config.py' \
  --prune-empty --tag-name-filter cat -- --all
```
3. Загрузите правильный файл без токена

## Готово! 🎉

Ваш проект теперь на GitHub!

**Следующие шаги:**
1. Добавьте скриншоты
2. Пригласите коллег посмотреть
3. Поделитесь ссылкой на репозиторий
4. Звезда ⭐ своему проекту!

---

**Нужна помощь?**
- [Git документация](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)

