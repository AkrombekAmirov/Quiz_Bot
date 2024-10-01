from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):  # Foydalanuvchi
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    name: str
    username: str
    phone_number: Optional[str] = None
    created_date: datetime = Field(default_factory=datetime.utcnow, index=True)


class Subject(SQLModel, table=True):  # Yunalish
    id: int = Field(default=None, primary_key=True)  # 1
    name: str  # Tarix
    subject_val: str  # Tarix


class Question(SQLModel, table=True):  # Savol
    id: int = Field(default=None, primary_key=True)
    subject_id: int
    text: str  # Amir Temur ning tugilgan yili
    created_date: datetime = Field(default_factory=datetime.utcnow)


class Answer(SQLModel, table=True):  # Javob
    id: int = Field(default=None, primary_key=True)
    text: str  # 1336
    question_id: int
    is_correct: bool


class Result(SQLModel, table=True):  # Natija
    id: int = Field(default=None, primary_key=True)
    user_id: int
    test_id: str
    subject_id: int
    question_ids: str
    correct_answers: int = Field(default=0)
    wrong_answers: int = Field(default=0)
    number: int = Field(default=0)
    status: bool = Field(default=False)
    created_date: datetime = Field(default_factory=datetime.utcnow)


class Test(SQLModel, table=True):  # Test
    id: int = Field(default=None, primary_key=True)
    user_id: int
    test_id: str
    subject_id: int
    question_id: int
    answer_id: int = Field(default=0)
    is_correct: bool = Field(default=False)
    created_date: datetime = Field(default_factory=datetime.utcnow)
