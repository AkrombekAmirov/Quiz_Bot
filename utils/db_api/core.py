from .models import User, Subject, Question, Result
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, Field, select
from sqlalchemy.exc import OperationalError
from typing import Optional, List, Type
from datetime import datetime
from json import dumps
import asyncio
import logging


# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class QuizDatabase:
    MAX_RETRIES = 3  # Bog'lanishni qayta urinishlar soni
    RETRY_DELAY = 2  # Qayta urinish orasidagi kutish vaqti (soniyada)

    def __init__(self, engine):
        self.engine = engine

    async def _add(self, instance: SQLModel):
        """Helper method to add an instance with retries in case of connection issues."""
        retries = 0
        while retries < self.MAX_RETRIES:
            async with AsyncSession(self.engine) as session:
                try:
                    async with session.begin():
                        session.add(instance)
                    await session.refresh(instance)
                    logging.info(f"Added: {instance}")
                    return instance.id
                except OperationalError as e:
                    logging.error(f"Database connection error on add attempt {retries + 1}: {e}")
                    retries += 1
                    await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    logging.error(f"Error adding instance: {e}")
                    break
        return None

    async def _update(self, instance: SQLModel):
        """Helper method to update an instance with retry logic."""
        retries = 0
        while retries < self.MAX_RETRIES:
            async with AsyncSession(self.engine) as session:
                try:
                    async with session.begin():
                        session.merge(instance)
                    await session.refresh(instance)
                    logging.info(f"Updated: {instance}")
                    return instance.id
                except OperationalError as e:
                    logging.error(f"Database connection error on update attempt {retries + 1}: {e}")
                    retries += 1
                    await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    logging.error(f"Error updating instance: {e}")
                    break
        return None

    async def add_user(self, user_id: int, name: str, username: str, phone_number: Optional[str] = None):
        return await self._add(User(user_id=user_id, name=name, username=username, phone_number=phone_number))

    async def add_subject(self, name: str, subject_val: int):
        return await self._add(Subject(name=name, subject_val=subject_val))

    async def add_question(self, subject_id: int, question: str, option1: str, option2: str, option3: str,
                           option4: str):
        return await self._add(
            Question(subject_id=subject_id, text=question, option1=option1, option2=option2, option3=option3,
                     option4=option4, correct_answer=option1))

    async def add_result(self, user_id: int, subject_id: int, question_ids):
        """
        Result jadvaliga yangi yozuv qo‘shadi. Savol IDlari JSON formatida saqlanadi.

        :param user_id: Foydalanuvchi ID
        :param subject_id: Fan ID
        :param question_ids: Savol IDlarining ro'yxati
        :param status: Test holati (boshlangan yoki tugatilgan)
        :return: Yangi yozuv IDsi yoki None
        """
        # _add yordamchi metodini chaqirish va yangi yozuv ID sini qaytarish
        return await self._add(Result(
            user_id=user_id,
            subject_id=subject_id,
            question_ids=question_ids,  # Savol IDlarini JSON formatiga o‘tkazish
            status=True
        ))

    async def get_user(self, user_id: int) -> Optional[User]:
        async with AsyncSession(self.engine) as session:
            try:
                statement = select(User).where(User.user_id == user_id)
                result = await session.execute(statement)
                return result.scalar_one_or_none()
            except OperationalError as e:
                logging.error(f"Database connection error on get_user: {e}")
                return None
            except Exception as e:
                logging.error(f"Error retrieving user: {e}")
                return None

    async def get_question(self, subject_id: int, text: str) -> Optional[Question]:
        """subject_id va text bo'yicha bitta savolni olish."""
        retries = 0
        while retries < self.MAX_RETRIES:
            async with AsyncSession(self.engine) as session:
                try:
                    # Filtrlangan savolni olish uchun so'rov
                    query = select(Question).where(
                        Question.subject_id == subject_id,
                        Question.text == text
                    )
                    result = await session.execute(query)
                    question = result.scalar_one_or_none()  # Agar natija topilmasa, None qaytaradi
                    await session.commit()  # Tranzaksiyani yopish
                    return question

                except OperationalError as e:
                    logging.error(f"Database connection error on get_question attempt {retries + 1}: {e}")
                    retries += 1
                    await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    logging.error(f"Error retrieving question: {e}")
                    break
        return None

    async def get_subject(self, name: str) -> Optional[Subject]:
        """subject_id va text bo'yicha bitta savolni olish."""
        retries = 0
        async with AsyncSession(self.engine) as session:
            while retries < self.MAX_RETRIES:
                try:
                    # Filtrlangan savolni olish uchun so'rov
                    query = select(Subject).where(Subject.name == name)
                    result = await session.execute(query)
                    question = result.scalar_one_or_none()  # Agar natija topilmasa, None qaytaradi
                    return question

                except OperationalError as e:
                    logging.error(f"Database connection error on get_subject attempt {retries + 1}: {e}")
                    retries += 1
                    await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    logging.error(f"Error retrieving subject: {e}")
                    break
        return None

    async def get(self, model: Type[SQLModel], filter_by: Optional[dict] = None, limit: Optional[int] = None) -> \
            Optional[List[SQLModel]]:
        """
        Ma'lumotlar bazasidan model asosida yozuvlarni olish uchun umumiy get funksiyasi.

        :param model: SQLModel turidagi model (jadval).
        :param filter_by: Filtlash shartlari (masalan, {"id": 1, "name": "John"}).
        :param limit: Qaytariladigan yozuvlar soni cheklovchi parametr.
        :return: Model yozuvlari ro'yxati yoki bo'sh ro'yxat.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            async with AsyncSession(self.engine) as session:
                try:
                    query = select(model)

                    # Filtrlash shartlarini qo'shish
                    if filter_by:
                        for key, value in filter_by.items():
                            if hasattr(model, key):  # Kalit mavjudligini tekshirish
                                query = query.where(getattr(model, key) == value)
                            else:
                                logging.warning(f"Invalid filter key: {key} for model {model.__name__}")

                    # Limit qo'llash
                    if limit:
                        query = query.limit(limit)

                    result = await session.execute(query)
                    records = result.scalars().all()
                    return records if records else []

                except OperationalError as e:
                    logging.error(f"Database connection error on get attempt {retries + 1}: {e}")
                    retries += 1
                    await asyncio.sleep(self.RETRY_DELAY)
                except Exception as e:
                    logging.error(f"Error retrieving data from {model.__name__}: {e}")
                    break
        return None

    async def get_result_id(self, result_id: int) -> Optional[SQLModel]:
        """
        result_id asosida natijani olish uchun yordamchi funksiya.

        :param result_id: Result jadvalidagi qatorning ID raqami.
        :return: Result obyekt yoki None agar topilmasa.
        """
        result = await self.get(model=Result, filter_by={"id": result_id}, limit=1)
        return result[0] if result else None
    async def get_result(self, user_id: int, subject_id: int):
        """
                Ma'lum `user_id` va `subject_id` bo'yicha `Result` jadvalidan yozuvni olish funksiyasi.

                :param user_id: Foydalanuvchi identifikatori.
                :param subject_id: Fan identifikatori.
                :return: Result obyekti yoki None.
                """
        return await self.get(model=Result, filter_by={"user_id": user_id, "subject_id": subject_id}, limit=1)

    async def user_update_test_id(self, user_id: int, test_id: str):
        async with AsyncSession(self.engine) as session:
            try:
                statement = select(User).where(User.user_id == user_id)
                result = await session.execute(statement)
                user = result.scalar_one_or_none()
                if user is None:
                    logging.warning(f"User not found: user_id={user_id}")
                    return None
                user.test_id = test_id
                await session.commit()
                await session.refresh(user)
                logging.info(f"Updated test_id for user_id={user_id}: {user.test_id}")
                return user.id
            except OperationalError as e:
                logging.error(f"Database connection error on user_update_test_id: {e}")
                return None
            except Exception as e:
                logging.error(f"Error updating test_id for user: {e}")
                return None

    # boshqa usullar ham xuddi shu tarzda qayta ishlanishi mumkin
