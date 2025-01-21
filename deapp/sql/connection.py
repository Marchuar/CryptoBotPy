import psycopg2
from psycopg2 import pool
import logging
from contextlib import contextmanager

# TODO Убрать в конфиг, создать постоянный файл .env на серваке
DB_HOST = "***REMOVED_DB_HOST***"
DB_NAME = "dedb"
DB_PASSWORD = "***REMOVED_DB_PASSWORD***"
DB_USERNAME = "root"
DB_PORT = "5432"
connection_pool = None


def initialize_connection_pool():
    """
    Initialize the connection pool.
    """
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,  # Minimum number of connections
            maxconn=10,  # Maximum number of connections
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        logging.info("Connection pool initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing connection pool: {e}")
        raise e


@contextmanager
def db_connection():
    conn = None
    cursor = None
    try:
        # Set a reasonable timeout for acquiring a connection
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except psycopg2.pool.PoolError as e:
        logging.error(f"Pool timeout: {e}")
        raise e
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Database operation error: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)


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
            logging.debug("Таблица users успешно создана или уже существует.")
    except Exception as e:
        logging.error(f"Ошибка при создании таблицы: {e}")
