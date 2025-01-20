import psycopg2
import logging
from contextlib import contextmanager

#TODO Убрать в конфиг, создать постоянный файл .env на серваке
DB_HOST = "dpg-cu77eedsvqrc7396mu1g-a.frankfurt-postgres.render.com"
DB_NAME = "dedb"
DB_PASSWORD = "mvDRhRJFojBzDP7dhQshPqkgT7hPpune"
DB_USERNAME = "root"
DB_PORT = "5432"

def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logging.ERROR(f"Ошибка подключения к базе данных: {e}")
        return None

@contextmanager
def db_connection():
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            raise Exception("Не удалось подключиться к базе данных")
        yield conn.cursor()
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logging.ERROR(f"Ошибка работы с базой данных: {e}")
        raise e
    finally:
        if conn:
            conn.close()

# Инициализация базы данных
def initialize_database():
    users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE NOT NULL,
            is_subscribed BOOLEAN DEFAULT FALSE,
            exchange_timeframe VARCHAR(10) DEFAULT NULL
        );
    """
    try:
        with db_connection() as cursor:
            cursor.execute(users_table_query)
            logging.DEBUG("Таблица users успешно создана или уже существует.")
    except Exception as e:
        logging.ERROR(f"Ошибка при создании таблицы: {e}")
