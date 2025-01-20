import logging
from sql.connection import db_connection


def db_add_user(user_id):
    try:
        with db_connection() as cursor:
            cursor.execute(
                "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                (user_id,)
            )
            logging.INFO(f"Новый пользователь успешно добавлен.")
    except Exception as e:
        logging.ERROR(f"Ошибка добавления пользователя {user_id}: {e}")


def tg_is_user_subscribed(user_id):
    with db_connection() as cursor:
        cursor.execute("SELECT is_subscribed FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else False


def db_user_exists(user_id):
    with db_connection() as cursor:
        cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone() is not None


def tg_subscribe_user(user_id):
    if db_user_exists(user_id):
        try:
            with db_connection() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET is_subscribed = TRUE
                    WHERE user_id = %s
            """, (user_id,))
        except Exception as e:
            logging.ERROR(f"Ошибка при попытке подписки на рассылку, user_id: {user_id}: {e}")
    else:
        try:
            with db_connection() as cursor:
                cursor.execute("""
                            INSERT INTO users (user_id, is_subscribed)
                            VALUES (%s, TRUE)
                        """, (user_id,))
        except Exception as e:
            logging.ERROR(f"Ошибка при попытке создания юзера + подписки на рассылку, user_id: {user_id}: {e}")


def tg_unsubscribe_user(user_id):
    try:
        with db_connection() as cursor:
            cursor.execute("""
            UPDATE users
            SET is_subscribed = FALSE,
            exchange_timeframe = NUll
            WHERE user_id = %s
        """, (user_id,))
    except Exception as e:
        logging.ERROR(f"Ошибка при попытке отписки на рассылку, user_id: {user_id}: {e}")
