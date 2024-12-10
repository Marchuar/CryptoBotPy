from telegram import Update, Bot
from telegram.ext import CallbackContext

bot = Bot("***REMOVED_TG_TOKEN***")
user_ids_ema = []
user_ids_bb = []
user_ids_macd = []


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет, DickiyEarning это инструмент для заработка !(огромного количества капусты)")

async def start_ema(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids_ema:
        await update.message.reply_text("Вы уже подписаны на рассылку EMA")
    else:
        user_ids_ema.append(user_id)
        await update.message.reply_text("Вы подписались на рассылку EMA")
        print(user_id)

async def start_bb(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids_bb:
        await update.message.reply_text("Вы уже подписаны на рассылку BB")
    else:
        user_ids_bb.append(user_id)
        await update.message.reply_text("Вы подписались на рассылку BB")
        print(user_id)

async def start_macd(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids_macd:
        await update.message.reply_text("Вы уже подписаны на рассылку MACD")
    else:
        user_ids_macd.append(user_id)
        await update.message.reply_text("Вы подписались на рассылку MACD")
        print(user_id)


async def stop(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id in user_ids_ema:
        user_ids_ema.remove(user_id)
        print(user_id)
        await update.message.reply_text("Вы отписались от рассылки EMA")
    elif user_id in user_ids_bb:
        user_ids_bb.remove(user_id)
        print(user_id)
        await update.message.reply_text("Вы отписались от рассылки BB")
    elif user_id in user_ids_macd:
        user_ids_macd.remove(user_id)
        print(user_id)
        await update.message.reply_text("Вы отписались от рассылки MACD")
    else:
        await update.message.reply_text("Вы ещё не получаете рассылки")