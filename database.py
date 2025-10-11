# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import config


class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                current_day INTEGER DEFAULT 0,
                certificate_first_name TEXT,
                certificate_last_name TEXT,
                awaiting_name_input INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица прогресса
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                day INTEGER,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                type TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, day, type)
            )
        ''')
        
        # Таблица достижений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_name TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, achievement_name)
            )
        ''')
        
        # Таблица фотографий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                photo_type TEXT,
                file_id TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # === USERS ===
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавить нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Пользователь уже существует
        finally:
            conn.close()
    
    def user_exists(self, user_id: int) -> bool:
        """Проверить существование пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить данные пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    
    def update_user_day(self, user_id: int, day: int):
        """Обновить текущий день пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET current_day = ? WHERE user_id = ?', (day, user_id))
        conn.commit()
        conn.close()
    
    def set_certificate_name(self, user_id: int, first_name: str, last_name: str = None):
        """Сохранить имя для сертификата"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET certificate_first_name = ?, certificate_last_name = ?
            WHERE user_id = ?
        ''', (first_name, last_name, user_id))
        conn.commit()
        conn.close()
    
    def get_certificate_name(self, user_id: int) -> Optional[str]:
        """Получить полное имя для сертификата"""
        user = self.get_user(user_id)
        if user and user['certificate_first_name']:
            if user['certificate_last_name']:
                return f"{user['certificate_first_name']} {user['certificate_last_name']}"
            return user['certificate_first_name']
        return None
    
    def set_awaiting_name_input(self, user_id: int, awaiting: bool):
        """Установить флаг ожидания ввода имени"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET awaiting_name_input = ? WHERE user_id = ?', (1 if awaiting else 0, user_id))
        conn.commit()
        conn.close()
    
    def is_awaiting_name_input(self, user_id: int) -> bool:
        """Проверить, ожидает ли бот ввода имени"""
        user = self.get_user(user_id)
        return user and user['awaiting_name_input'] == 1
    
    # === PROGRESS ===
    
    def mark_day_completed(self, user_id: int, day: int, day_type: str = 'workout'):
        """Отметить день как выполненный"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO progress (user_id, day, completed, completed_at, type)
                VALUES (?, ?, 1, ?, ?)
                ON CONFLICT(user_id, day, type) 
                DO UPDATE SET completed = 1, completed_at = ?
            ''', (user_id, day, datetime.now(), day_type, datetime.now()))
            conn.commit()
        finally:
            conn.close()
    
    def is_day_completed(self, user_id: int, day: int, day_type: str = 'workout') -> bool:
        """Проверить выполнен ли день"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT completed FROM progress 
            WHERE user_id = ? AND day = ? AND type = ?
        ''', (user_id, day, day_type))
        result = cursor.fetchone()
        conn.close()
        return result and result['completed'] == 1
    
    def get_user_progress(self, user_id: int) -> Dict:
        """Получить прогресс пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Всего выполненных дней
        cursor.execute('''
            SELECT COUNT(*) as total FROM progress 
            WHERE user_id = ? AND completed = 1
        ''', (user_id,))
        total_completed = cursor.fetchone()['total']
        
        # Выполненные тренировки
        cursor.execute('''
            SELECT COUNT(*) as total FROM progress 
            WHERE user_id = ? AND completed = 1 AND type = 'workout'
        ''', (user_id,))
        workouts = cursor.fetchone()['total']
        
        # Выполненные задания
        cursor.execute('''
            SELECT COUNT(*) as total FROM progress 
            WHERE user_id = ? AND completed = 1 AND type = 'task'
        ''', (user_id,))
        tasks = cursor.fetchone()['total']
        
        conn.close()
        
        # Подсчет баллов (каждый день/задание = 1 балл)
        points = total_completed
        
        # Процент выполнения (21 тренировочный день + 9 заданий + фото до/после = 32 активности)
        total_activities = 32
        percentage = int((total_completed / total_activities) * 100) if total_completed > 0 else 0
        
        return {
            'total_completed': total_completed,
            'workouts': workouts,
            'tasks': tasks,
            'points': points,
            'percentage': percentage
        }
    
    def get_completed_tabata_count(self, user_id: int) -> int:
        """Получить количество выполненных табата тренировок"""
        tabata_days = [1, 5, 12, 19]  # Дни с табатой
        conn = self.get_connection()
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(tabata_days))
        cursor.execute(f'''
            SELECT COUNT(*) as total FROM progress 
            WHERE user_id = ? AND day IN ({placeholders}) AND completed = 1 AND type = 'workout'
        ''', (user_id, *tabata_days))
        result = cursor.fetchone()
        conn.close()
        return result['total']
    
    def get_completed_glutes_count(self, user_id: int) -> int:
        """Получить количество выполненных тренировок на ягодицы"""
        glutes_days = [5, 10, 17]  # Дни с ягодицами
        conn = self.get_connection()
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(glutes_days))
        cursor.execute(f'''
            SELECT COUNT(*) as total FROM progress 
            WHERE user_id = ? AND day IN ({placeholders}) AND completed = 1 AND type = 'workout'
        ''', (user_id, *glutes_days))
        result = cursor.fetchone()
        conn.close()
        return result['total']
    
    # === ACHIEVEMENTS ===
    
    def add_achievement(self, user_id: int, achievement_name: str):
        """Добавить достижение"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO achievements (user_id, achievement_name)
                VALUES (?, ?)
            ''', (user_id, achievement_name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Достижение уже получено
        finally:
            conn.close()
    
    def has_achievement(self, user_id: int, achievement_name: str) -> bool:
        """Проверить наличие достижения"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM achievements 
            WHERE user_id = ? AND achievement_name = ?
        ''', (user_id, achievement_name))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Получить все достижения пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT achievement_name, unlocked_at 
            FROM achievements 
            WHERE user_id = ? 
            ORDER BY unlocked_at
        ''', (user_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # === PHOTOS ===
    
    def add_photo(self, user_id: int, photo_type: str, file_id: str):
        """Добавить фотографию"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO photos (user_id, photo_type, file_id)
            VALUES (?, ?, ?)
        ''', (user_id, photo_type, file_id))
        conn.commit()
        conn.close()
    
    def has_photo(self, user_id: int, photo_type: str) -> bool:
        """Проверить наличие фото"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM photos 
            WHERE user_id = ? AND photo_type = ?
        ''', (user_id, photo_type))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def get_photo(self, user_id: int, photo_type: str) -> Optional[dict]:
        """Получить фото (file_id и дата загрузки)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT file_id, uploaded_at FROM photos 
            WHERE user_id = ? AND photo_type = ?
            ORDER BY uploaded_at DESC
            LIMIT 1
        ''', (user_id, photo_type))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'file_id': result['file_id'],
                'uploaded_at': result['uploaded_at']
            }
        return None
    
    # === COMPLETION CHECK ===
    
    def check_100_percent_completion(self, user_id: int) -> bool:
        """Проверить 100% выполнение интенсива"""
        # Проверяем наличие фото до и после
        has_before = self.has_photo(user_id, 'before')
        has_after = self.has_photo(user_id, 'after')
        
        if not (has_before and has_after):
            return False
        
        # Проверяем выполнение всех тренировок (дни: 1,3,5,7,8,10,12,14,15,17,19,21)
        workout_days = [1, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 21]
        for day in workout_days:
            if not self.is_day_completed(user_id, day, 'workout'):
                return False
        
        # Проверяем выполнение всех заданий (дни: 2,4,6,9,11,13,16,18,20)
        task_days = [2, 4, 6, 9, 11, 13, 16, 18, 20]
        for day in task_days:
            if not self.is_day_completed(user_id, day, 'task'):
                return False
        
        return True


# Глобальный экземпляр базы данных
db = Database()

