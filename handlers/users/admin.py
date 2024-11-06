from keyboards import admin_menu, yonalish_nomi_keyboard, list_faculty, faculty_file_map2
from file_service import join_file, read_file, get_path
from utils.db_api.core import QuizDatabase
from aiogram.dispatcher import FSMContext
from aiogram import types
from states import User
from data import engine
from loader import dp

db = QuizDatabase(engine=engine)


@dp.message_handler(commands=["admin"])
async def admin(message: types.Message):
    await message.answer("Admin panelga keldingiz\nXizmat turini tanlang", reply_markup=admin_menu)


@dp.callback_query_handler(lambda call: call.data == "admin_add_test")
async def admin_add_department(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Yo'nalishni tanlang", reply_markup=yonalish_nomi_keyboard)
    await User.zero.set()


@dp.callback_query_handler(lambda call: call.data in list_faculty, state=User.zero)
async def admin_add_subject(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"faculty_": call.data})
    await call.message.answer("Tast tayyorlangan fileni yuboring!\nEslatma file nomiga etibor bering!")
    await User.one.set()


@dp.message_handler(content_types=types.ContentTypes.DOCUMENT, state=User.one)
async def handle_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    subject_id = await db.get_subject(name=faculty_file_map2.get(data["faculty_"]))
    print(subject_id.subject_val)
    await dp.bot.download_file(
        (await dp.bot.get_file(message.document.file_id)).file_path,
        await join_file(file_name=message.document.file_name)
    )
    await message.answer("Fayl saqlandi!")
    if await read_file(file_path=message.document.file_name, subject_id=int(subject_id.subject_val)):
        await message.answer("Testlar bazasiga qo'shildi", reply_markup=admin_menu)
        await state.reset_state(with_data=False)
    else:
        await message.answer("Qayta urinib ko'ring!", reply_markup=list_faculty)
        await User.zero.set()