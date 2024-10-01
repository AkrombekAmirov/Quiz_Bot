from keyboards.inline import keyboard_user
from utils.db_api.core import QuizDatabase
from aiogram.dispatcher import FSMContext
from data.config import engine
from aiogram import types
from random import sample
from uuid import uuid4
from loader import dp

db = QuizDatabase(engine=engine)


@dp.callback_query_handler(lambda call: call.data == "test")
async def start(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"user_id": call.from_user.id})
    if db.get_user(user_id=call.from_user.id):
        await call.message.answer("Testni boshlash", reply_markup=keyboard_user.yonalish_nomi_keyboard)
    else:
        await call.message.answer("Telegram raqamingizni yuboring.", reply_markup=keyboard_user.keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def test(message: types.Message, state: FSMContext):
    if not db.get_user(user_id=message.from_user.id):
        db.add_user(user_id=message.from_user.id, name=message.from_user.full_name, username=message.from_user.username,
                    phone_number=message.contact.phone_number)
    await state.update_data({"phone": message.contact.phone_number})
    await message.answer("Testni boshlash", reply_markup=keyboard_user.yonalish_nomi_keyboard)


@dp.callback_query_handler(
    lambda call: call.data in ["faculty0", "faculty1", "faculty2", "faculty3", "faculty4", "faculty5", "faculty6"])
async def test(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"faculty": call.data})
    data = call.data
    l = []
    print(data)
    print(db.get_subject(subject_val=data).id)
    print(db.get_questions(subject_id=db.get_subject(subject_val=data).id))
    _uuid = str(uuid4())

    for i in db.get_questions(subject_id=db.get_subject(subject_val=data).id):
        l.append(i.id)
        print(i.id)
    test_numbers = sample(l, 5)
    if db.check_reslt(user_id=call.from_user.id, status=True):
        print(db.check_reslt(user_id=call.from_user.id, status=True))
        print("Ruxsat etilgan")
    # db.add_result(user_id=call.from_user.id, test_id=_uuid, subject_id=db.get_subject(subject_val=data).id,
    #               question_ids=str(test_numbers))
    # for i in test_numbers:
    #     db.add_test(user_id=call.from_user.id, test_id=_uuid, subject_id=db.get_subject(subject_val=data).id,
    #                 question_id=i)
    await call.message.answer('test', reply_markup=keyboard_user.yonalish_nomi_keyboard)
