from sql.commands import tg_is_user_subscribed, tg_subscribe_user, tg_unsubscribe_user, tg_update_user_timeframe, tg_get_user_timeframe
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
available_timeframes = ['15m', '30m', '4h', '1d']

timeframe_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=available_timeframes[0], callback_data='15m')],
    [InlineKeyboardButton(text=available_timeframes[1], callback_data='30m')],
    [InlineKeyboardButton(text=available_timeframes[2], callback_data='4h')],
    [InlineKeyboardButton(text=available_timeframes[3], callback_data='1d')]
])

@router.message(CommandStart())
async def cmd_start(message: Message):
    await start(message)

@router.message(Command('stop'))
async def cmd_stop(message: Message):
    await stop(message)

@router.message(Command('timeframe'))
async def change_timeframe(message: Message):
    await message.answer("Choose timeframe:", reply_markup=timeframe_settings)

@router.callback_query(lambda c: c.data in available_timeframes)
async def process_timeframe_callback(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    selected_timeframe = callback_query.data

    tg_update_user_timeframe(user_id, selected_timeframe)
    await callback_query.message.answer("Saved")

async def start(message: Message):
    user_id = message.from_user.id
    if tg_is_user_subscribed(user_id):
        await message.answer("Вы уже подписаны на рассылку")
    else:
        tg_subscribe_user(user_id)
        await message.answer("Вы подписались на рассылку")

async def stop(message: Message):
    user_id = message.from_user.id
    if tg_is_user_subscribed(user_id):
        tg_unsubscribe_user(user_id)
        await message.answer("Вы отписались от рассылки")
    else:
        await message.answer("Вы ещё не получаете рассылки")

async def send_signal(message):
    await router.