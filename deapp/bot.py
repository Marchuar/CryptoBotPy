from telegram import Update, Bot
from telegram.ext import CallbackContext

bot = Bot("***REMOVED_TG_TOKEN***")
user_ids = []


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids:
        await update.message.reply_text("Вы уже подписаны на рассылку")
    else:
        user_ids.append(user_id)
        await update.message.reply_text("Вы подписались на рассылку")
        print(user_id)


async def stop(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids:
        user_ids.remove(user_id)
        print(user_id)
        await update.message.reply_text("Вы отписались от рассылки")
    else:
        await update.message.reply_text("Вы ещё не получаете рассылки")