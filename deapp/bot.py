import logging

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
import config
from sql.commands import tg_is_user_subscribed, tg_subscribe_user, tg_unsubscribe_user, tg_update_user_timeframe, tg_get_user_timeframe

bot = Bot("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if tg_is_user_subscribed(user_id):
        await update.message.reply_text("Вы уже подписаны на рассылку")
    else:
        tg_subscribe_user(user_id)
        await update.message.reply_text("Вы подписались на рассылку")

async def change_timeframe(update: Update, context: CallbackContext):
    # добавить возможность изменять timeframe у каждого user отдельно
    # user_id = update.effective_chat.id

    # Создаём кнопки для тг
    keyboard = [
            [
                InlineKeyboardButton("5 минут", callback_data="5m"),
                InlineKeyboardButton("15 минут", callback_data="15m"),
                InlineKeyboardButton("30 минут", callback_data="30m"),
            ],
            [
                InlineKeyboardButton("1 час", callback_data="1h"),
                InlineKeyboardButton("4 часа", callback_data="4h"),
                InlineKeyboardButton("1 день", callback_data="1d"),
            ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.message.reply_text("Выберите таймфрейм:", reply_markup=reply_markup)

async def timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Обязательно вызываем, чтобы убрать "крутящийся кружок"

    # Извлекаем значение таймфрейма
    user_id = update.effective_chat.id
    tg_update_user_timeframe(user_id, query.data)

    # Отвечаем пользователю
    await query.edit_message_text(f"Вы выбрали таймфрейм: {tg_get_user_timeframe(user_id)}")

async def stop(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if tg_is_user_subscribed(user_id):
        tg_unsubscribe_user(user_id)
        await update.message.reply_text("Вы отписались от рассылки")
    else:
        await update.message.reply_text("Вы ещё не получаете рассылки")