import logging

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
import config

bot = Bot("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")
user_ids = []


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids:
        await update.message.reply_text("Вы уже подписаны на рассылку")
    else:
        user_ids.append(user_id)
        await update.message.reply_text("Вы подписались на рассылку")
        logging.info(user_id)

async def change_timeframe(update: Update, context: CallbackContext):
    # добавить возможность изменять timeframe у каждого user отдельно
    # user_id = update.effective_chat.id

    # Создаём кнопки для тг
    keyboard = [
            [
                InlineKeyboardButton("5 минут", callback_data="5m"),
                InlineKeyboardButton("30 минут", callback_data="30m"),
            ],
            [
                InlineKeyboardButton("1 час", callback_data="1h"),
                InlineKeyboardButton("4 часа", callback_data="4h"),
            ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками
    await update.message.reply_text("Выберите таймфрейм:", reply_markup=reply_markup)

async def timeframe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Обязательно вызываем, чтобы убрать "крутящийся кружок"

    # Извлекаем значение таймфрейма
    selected_timeframe = query.data

    # Изменяем timeframe
    config.TIMEFRAME = selected_timeframe

    # Отвечаем пользователю
    await query.edit_message_text(f"Вы выбрали таймфрейм: {selected_timeframe}")

async def stop(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids:
        user_ids.remove(user_id)
        logging.info(user_id)
        await update.message.reply_text("Вы отписались от рассылки")
    else:
        await update.message.reply_text("Вы ещё не получаете рассылки")