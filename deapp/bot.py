import logging

from telegram import Update, Bot
from telegram.ext import CallbackContext

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

async def stop(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids:
        user_ids.remove(user_id)
        logging.info(user_id)
        await update.message.reply_text("Вы отписались от рассылки")
    else:
        await update.message.reply_text("Вы ещё не получаете рассылки")