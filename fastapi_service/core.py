from ..utils.db_api.core import QuizDatabase
from data.config import engine
from fastapi import FastAPI
from typing import List

app = FastAPI()
db = QuizDatabase(engine)

__all__ = ["app", "db"]


@app.post("/create_subject")
async def create_subject(name: str):
    return await db.add_subject(name=name)


@app.post("/create_question")
async def create_question(subject_id: int, question_text: str, answers: List[dict]):
    return await db.add_question_with_answers(subject_id=subject_id, question_text=question_text, answers=answers)
