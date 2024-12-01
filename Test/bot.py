from telegram import Update, Bot
from telegram.ext import CallbackContext
import time
import price
import order

bot = Bot("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")
userIds = []


def start(update: Update, context: CallbackContext):
    userId = update.effective_chat.id
    if userId in userIds:
        update.message.reply_text("Вы уже подписаны на рассылку")
    else:
        userIds.append(userId)
        update.message.reply_text("Вы подписались на рассылку")
        print(userId)


def stop(update: Update, context: CallbackContext):
    userId = update.effective_chat.id
    if userId in userIds:
        userIds.remove(userId)
        print(userId)
        update.message.reply_text("Вы отписались от рассылки")
    else:
        update.message.reply_text("Вы ещё не получаете рассылки")


def orders(update: Update, context: CallbackContext):
    response = order.getOrdersInfo()
    update.message.reply_text(response)


def sendMessage():
    while True:
        price.get10Prices()
        for id in userIds:
            try:
                bot.send_message(chat_id=id, text=price.pricesList)
                price.pricesList.clear()
                print("sended")
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(10)