import logging
from sql.connection import db_connection


def db_add_user(user_id):
    try:
        with db_connection() as cursor:
            cursor.execute(
                "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", (user_id,)
            )
            logging.info(f"New user successfully added.")
    except Exception as e:
        logging.error(f"Error adding a user {user_id}: {e}")


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
                    SET is_subscribed = TRUE,
                    exchange_timeframe = '1h'
                    WHERE user_id = %s
            """, (user_id,))
        except Exception as e:
            logging.error(f"Error when trying to subscribe to the alerting, user_id: {user_id}: {e}")
    else:
        try:
            with db_connection() as cursor:
                cursor.execute("""
                            INSERT INTO users (user_id, is_subscribed)
                            VALUES (%s, TRUE)
                        """, (user_id,))
        except Exception as e:
            logging.error(f"Error when trying to create a user + subscription to the alerting, user_id: {user_id}: {e}")


def tg_unsubscribe_user(user_id):
    try:
        with db_connection() as cursor:
            cursor.execute("""
            UPDATE users
            SET is_subscribed = FALSE
            WHERE user_id = %s
        """, (user_id,))
    except Exception as e:
        logging.error(f"Error when trying to unsubscribe from the alerting, user_id: {user_id}: {e}")


def tg_update_user_timeframe(user_id, timeframe):
    try:
        with db_connection() as cursor:
            cursor.execute("""
                UPDATE users
                SET exchange_timeframe = %s
                WHERE user_id = %s
            """, (timeframe, user_id))
    except Exception as e:
        logging.error(f"Error when trying to unsubscribe from the alerting, user_id: {user_id}: {e}")


def tg_get_user_timeframe(user_id):
    with db_connection() as cursor:
        cursor.execute("""
                SELECT exchange_timeframe
                FROM users
                WHERE user_id = %s
            """, (user_id,))
        result = cursor.fetchone()
        return result[0]

def db_get_subscribed_users():
    with db_connection() as cursor:
        cursor.execute("""
                SELECT user_id
                FROM users
                WHERE is_subscribed = TRUE
            """)
        result = cursor.fetchall()
        return [row[0] for row in result]

