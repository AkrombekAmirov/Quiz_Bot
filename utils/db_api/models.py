from PIL.ImImagePlugin import number
from sqlmodel import SQLModel, Field, Relationship, Session, Column, JSON, TEXT
from typing import Optional, List
from datetime import datetime
from functools import wraps
from pytz import timezone
import logging
import json

# Logger konfiguratsiyasi
logging.basicConfig(level=logging.INFO)


# Xatoliklarni boshqarish uchun dekorator
def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise

    return wrapper


class BaseModel(SQLModel):
    """Yana foydalanishga yaroqli bazaviy model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_date: str = Field(default_factory=lambda: datetime.now(timezone('Asia/Tashkent')).strftime("%Y-%m-%d"),
                              description="Yaratilgan sana")
    created_time: str = Field(default_factory=lambda: datetime.now(timezone('Asia/Tashkent')).strftime("%H:%M:%S"),
                              description="Yaratilgan vaqt")


class User(BaseModel, table=True):  # Foydalanuvchi
    __tablename__ = 'users'
    user_id: str = Field(..., unique=True, description="Foydalanuvchi ID")
    name: str = Field(..., description="Foydalanuvchi ismi")
    username: str = Field(..., description="Foydalanuvchi nomi")
    phone_number: Optional[str] = Field(default=None, description="Telefon raqami")
    # results: List["Result"] = Relationship(back_populates="user")


class Subject(BaseModel, table=True):  # Fan
    __tablename__ = 'subjects'
    name: str = Field(..., description="Fan nomi")
    subject_val: str = Field(..., description="Fan qiymati")
    # questions: List["Question"] = Relationship(
    #     back_populates="subject")  # `questions` bilan `back_populates` o'rnatildi
    # results: List["Result"] = Relationship(back_populates="subject")  # `results` bilan `back_populates` o'rnatildi


class Question(BaseModel, table=True):  # Savol
    __tablename__ = 'questions'
    subject_id: int = Field(..., description="Fan ID")
    text: str = Field(..., description="Savol matni")
    option1: str = Field(..., description="Javob variantlari")
    option2: str = Field(..., description="Javob variantlari")
    option3: str = Field(..., description="Javob variantlari")
    option4: str = Field(..., description="Javob variantlari")
    correct_answer: str = Field(..., description="To'g'ri javob")
    # subject: Optional["Subject"] = Relationship(back_populates="questions")  # `subject` bilan `Relationship` o'rnatildi


class Result(BaseModel, table=True):  # Natija
    __tablename__ = 'results'
    user_id: str = Field(..., description="Foydalanuvchi ID")
    subject_id: int = Field(..., description="Fan ID")
    question_ids: str = Field(sa_column=Column(TEXT), description="Savol ID larining ro'yxati JSON formatida")
    correct_answers: int = Field(default=0, description="To'g'ri javoblar soni")
    wrong_answers: int = Field(default=0, description="Noto'g'ri javoblar soni")
    number: int = Field(default=0, description="Test holati uchun")
    status: bool = Field(default=False, description="Test holati")

    # Foydalanuvchi va Fan bilan bog'lanish
    # user: Optional["User"] = Relationship(back_populates="results")  # `results` bilan o'rnatildi
    # subject: Optional["Subject"] = Relationship(back_populates="results")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def set_question_ids(self, ids: List[int]) -> None:
        """question_ids uchun JSON formatida ro‘yxatni saqlaydi."""
        self.question_ids = json.dumps(ids)

    def get_question_ids(self) -> List[int]:
        """JSON formatidagi question_ids qiymatini ro‘yxat sifatida qaytaradi."""
        return json.loads(self.question_ids) if self.question_ids else []

    def update_score(self, correct: int, wrong: int) -> None:
        """Natijalarni yangilaydi."""
        self.correct_answers += correct
        self.wrong_answers += wrong
        self.number += (correct + wrong)

    def accuracy(self) -> float:
        """To‘g‘ri javoblar foizini qaytaradi."""
        total_answers = self.correct_answers + self.wrong_answers
        return (self.correct_answers / total_answers) * 100 if total_answers > 0 else 0

    def is_passed(self) -> bool:
        """Testdan o‘tish holatini tekshiradi."""
        return self.accuracy() >= 50

    def to_summary(self) -> dict:
        """Natijalar haqida qisqacha ma'lumot."""
        return {
            "user_id": self.user_id,
            "test_id": self.id,
            "accuracy": self.accuracy(),
            "status": self.status,
            "created_date": self.created_date.isoformat()
        }
