from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import time
import price
import threading
import order

userIds = []


def start(update: Update, context: CallbackContext):
    userId = update.effective_chat.id
    if userId in userIds:
        update.message.reply_text("Вы уже подписаны на рассылку")
    else:
        userIds.append(userId)
        update.message.reply_text("Вы подписались на рассылку")
        print(userId)


def orders(update: Update, context: CallbackContext):
    response = order.getOrdersInfo()
    update.message.reply_text(response)


def sendMessage():
    price.get20Prices()

    bot = Bot("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")

    for id in userIds:
        try:
            bot.send_message(chat_id=id, text=price.pricesList)
            print("sended")
        except Exception as e:
            print(f"Error: {e}")


def main():
    updater = Updater("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")
    dp = updater.dispatcher

    # add start command
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("orders", orders))

    threading.Thread(target=sendMessage, daemon=True).start()

    # start bot
    updater.start_polling()
    updater.idle()


main()
