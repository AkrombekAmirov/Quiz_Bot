from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards import admin_menu, for_user
from loader import dp
from data import ADMINS


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    if str(message.from_user.id) == str(ADMINS):
        await message.answer(f"Salom, {message.from_user.full_name}!", reply_markup=admin_menu)
    else:
        await message.answer(f"Salom, {message.from_user.full_name}!", reply_markup=for_user)
