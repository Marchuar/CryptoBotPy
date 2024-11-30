from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import time
import price
import threading
import order
import analyzeMarket

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

        bot = Bot("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")

        for id in userIds:
            try:
                bot.send_message(chat_id=id, text=price.pricesList)
                price.pricesList.clear()
                print("sended")
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(10)


def main():
    updater = Updater("7220502529:AAFNYqjEqtTPMYlBW0PoZkAa7WWD79mXJ1c")
    dp = updater.dispatcher

    # add start command
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("orders", orders))

    # prices
    # threading.Thread(target=sendMessage, daemon=True).start()

    # analyze market
    threading.Thread(
        target=analyzeMarket.fetchData, args=(userIds,), daemon=True
    ).start()

    # start bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
