from utils.db_api.core import QuizDatabase
from enum import Enum
from data.config import engine
from fastapi import FastAPI
from typing import List

app = FastAPI()
db = QuizDatabase(engine)

__all__ = ["app", "db"]


class Direct(Enum):
    Tarix = 1
    Fizika = 2
    Kimyo = 3
    Ingliz = 4
    Matematika = 5
    Biologiya = 6
    Geografiya = 7


@app.post("/create_subject")
async def create_subject(name: str):
    return db.add_subject(name=name)


@app.post(f"/create_question_one", )
async def create_question(subject_id: int, question_text: str, answers1: str, answers2: str, answers3: str, answers4: str):
    answers = [{"text": answers1, "is_correct": True}, {"text": answers2, "is_correct": False},
               {"text": answers3, "is_correct": False}, {"text": answers4, "is_correct": False}]
    print('sadsadsad')
    return db.add_question_with_answers(subject_id=subject_id, question_text=question_text, answers=answers)


@app.post(f"/create_question_two", )
async def create_question(question_text: str, answers1: str, answers2: str, answers3: str, answers4: str):
    answers = [{"text": answers1, "is_correct": True}, {"text": answers2, "is_correct": False},
               {"text": answers3, "is_correct": False}, {"text": answers4, "is_correct": False}]
    return db.add_question_with_answers(subject_id=5, question_text=question_text, answers=answers)


@app.post(f"/create_question_three", )
async def create_question(question_text: str, answers1: str, answers2: str, answers3: str, answers4: str):
    answers = [{"text": answers1, "is_correct": True}, {"text": answers2, "is_correct": False},
               {"text": answers3, "is_correct": False}, {"text": answers4, "is_correct": False}]
    return db.add_question_with_answers(subject_id=6, question_text=question_text, answers=answers)


@app.post(f"/create_question_four", )
async def create_question(question_text: str, answers1: str, answers2: str, answers3: str, answers4: str):
    answers = [{"text": answers1, "is_correct": True}, {"text": answers2, "is_correct": False},
               {"text": answers3, "is_correct": False}, {"text": answers4, "is_correct": False}]
    return db.add_question_with_answers(subject_id=7, question_text=question_text, answers=answers)