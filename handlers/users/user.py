from keyboards import keyboard_user, faculty_file_map2
from sqlmodel.ext.asyncio.session import AsyncSession
from utils import QuizDatabase, Question, Result
from aiogram.dispatcher import FSMContext
from data.config import engine
from aiogram import types
from loader import dp
import random
import json
from sqlmodel import select

db = QuizDatabase(engine=engine)


@dp.callback_query_handler(lambda call: call.data == "test")
async def start(call: types.CallbackQuery, state: FSMContext):
    await state.update_data({"user_id": call.from_user.id})
    if await db.get_user(user_id=call.from_user.id):
        await call.message.answer("Testni boshlash", reply_markup=keyboard_user.yonalish_nomi_keyboard)
    else:
        await call.message.answer("Telegram raqamingizni yuboring.", reply_markup=keyboard_user.keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def test(message: types.Message, state: FSMContext):
    if not await db.get_user(user_id=message.from_user.id):
        await db.add_user(user_id=message.from_user.id, name=message.from_user.full_name,
                          username=message.from_user.username,
                          phone_number=message.contact.phone_number)
    await state.update_data({"phone": message.contact.phone_number})
    await message.answer("Testni boshlash", reply_markup=keyboard_user.yonalish_nomi_keyboard)


@dp.callback_query_handler(
    lambda call: call.data in ["faculty0", "faculty1", "faculty2", "faculty3", "faculty4", "faculty5", "faculty6"]
)
async def start_test(call: types.CallbackQuery, state: FSMContext):
    """Yo'nalishni tanlagandan so'ng testni boshlash yoki davom ettirish."""
    user_id = call.from_user.id
    await state.update_data({"faculty": call.data})

    # Yo'nalishni olish
    sub = await db.get_subject(faculty_file_map2.get(call.data))

    if sub is not None:
        # Test natijasi mavjudligini tekshirish
        result = await db.get_result(user_id=user_id, subject_id=sub.id)
        print(result)

        if result and result.status:
            # Test davom ettiriladi
            questions = await db.get(model=Question, filter_by={"subject_id": int(sub.subject_val)})
            selected_questions = [q for q in questions if q.id in json.loads(result.question_ids)]
            current_index = int(result.number)
            await state.update_data({
                "result_id": result.id,
                "questions": selected_questions,
                "current_index": current_index
            })
        else:
            # Yangi test boshlanadi
            all_questions = await db.get(model=Question, filter_by={"subject_id": int(sub.subject_val)})
            selected_questions = random.sample(all_questions, k=15)

            # Test natijasini `Result` jadvalida boshlash
            await db.add_result(
                user_id=user_id,
                subject_id=sub.id,
                question_ids=json.dumps([q.id for q in selected_questions])
            )
            await state.update_data({
                "result_id": result.id,
                "questions": selected_questions,
                "current_index": 0
            })

        # Birinchi savolni yuborish
        await send_question(call.message, state)
    else:
        await call.message.answer("Tanlangan yo'nalish mavjud emas.")



async def send_question(message: types.Message, state: FSMContext):
    """Foydalanuvchiga savolni va random aralashtirilgan javob variantlarini yuborish."""
    data = await state.get_data()
    questions = data["questions"]
    current_index = data["current_index"]

    if current_index >= len(questions):
        # Test yakunlanganda natijani chiqarish
        await end_test(message, state)
        return

    question = questions[current_index]

    # Variantlarni aralashtirish
    options = [question.correct_answer, question.option2, question.option3, question.option4]
    random.shuffle(options)  # Javob variantlarini random tartibda aralashtirish

    # Aralashtirilgan variantlar bilan savolni yuborish
    keyboard = types.InlineKeyboardMarkup()
    for index, option in enumerate(options):
        # Indeks orqali `callback_data` ni o‘rnatish
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=f"answer_{index}"))

    # To‘g‘ri javob indeksini holatda saqlash
    correct_option_index = options.index(question.correct_answer)
    await state.update_data({
        "correct_option_index": correct_option_index,
        "current_index": current_index
    })
    await message.edit_text(question.text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith("answer_"))
async def handle_answer(call: types.CallbackQuery, state: FSMContext):
    """Foydalanuvchi javobini qayta ishlash va natijani yangilash."""
    data = await state.get_data()
    current_index = data["current_index"]
    result_id = data["result_id"]

    # Foydalanuvchi tanlagan javobni olish
    selected_option_index = int(call.data.split("_")[1])  # Foydalanuvchi tanlagan indeks
    correct_option_index = data["correct_option_index"]  # To‘g‘ri javobning indeksi

    is_correct = selected_option_index == correct_option_index

    # To‘g‘ri yoki noto‘g‘ri javobni bildiruvchi xabar
    if is_correct:
        await call.answer("To‘g‘ri javob! ✅")
    else:
        await call.answer("Noto‘g‘ri javob. ❌")

    # `Result` jadvalidagi natijalarni yangilash
    async with AsyncSession(engine) as session:
        result = await db.get_result_id(result_id)
        if result:
            if is_correct:
                result.correct_answers += 1
            else:
                result.wrong_answers += 1
            result.number += 1  # Hozirgi savol raqamini yangilash
            await session.commit()

            # Test yakunlangani tekshirish
            if result.number >= 15:
                await end_test(call.message, state)
                return

    # Keyingi savolga o'tish
    await state.update_data({"current_index": current_index + 1})
    await send_question(call.message, state)


async def end_test(message: types.Message, state: FSMContext):
    """Test tugagach foydalanuvchiga natijani ko'rsatish."""
    data = await state.get_data()
    result_id = data["result_id"]

    # Natijalarni bazadan olish va foydalanuvchiga xabar yuborish
    async with AsyncSession(engine) as session:
        result = await session.get(Result, result_id)
        if result:
            accuracy = result.accuracy()
            status_msg = "O'tdingiz!" if result.status else "O'tmadingiz."
            summary = (
                f"Test yakunlandi!\n"
                f"To'g'ri javoblar: {result.correct_answers}\n"
                f"Noto'g'ri javoblar: {result.wrong_answers}\n"
                f"Umumiy savollar: {result.number}\n"
                f"Samaradorlik: {accuracy:.2f}%\n"
                f"Natija: {status_msg}"
            )
            await message.edit_text(summary)

            # Testni tugatish va `status` ni `False` qilish
            result.status = False
            await session.commit()

    # Test holatini tugatish
    await state.finish()
