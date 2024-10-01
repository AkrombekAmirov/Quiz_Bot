from sqlmodel import SQLModel, create_engine, Session, select
from datetime import datetime
from typing import Optional, List
from .models import User, Subject, Question, Answer, Result, Test


class QuizDatabase:
    def __init__(self, engine):
        self.engine = engine

    def _add(self, instance):
        """Helper method to add an instance to the session and commit."""
        with Session(self.engine) as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            print(f"Added: {instance}")
        return instance.id

    def add_user(self, user_id: int, name: str, username: str, phone_number: Optional[str] = None):
        return self._add(User(user_id=user_id, name=name, username=username, phone_number=phone_number))

    def get_user(self, user_id: int) -> Optional[User]:
        with Session(self.engine) as session:
            statement = select(User).where(User.user_id == user_id)
            result = session.exec(statement)
            return result.one_or_none()

    def add_subject(self, name: str, subject_val: str):
        return self._add(Subject(name=name, subject_val=subject_val))

    def get_subject(self, subject_val: int) -> Optional[Question]:
        with Session(self.engine) as session:
            statement = select(Subject).where(Subject.subject_val == subject_val)
            result = session.exec(statement)
            return result.one_or_none()

    def add_question_with_answers(self, subject_id: int, question_text: str, answers: List[dict]):
        """
        Add a question along with its answer options.

        :param subject_id: ID of the subject the question belongs to.
        :param question_text: The question text.
        :param answers: List of dictionaries containing answer text and correctness.
                        Example: [{'text': 'Answer 1', 'is_correct': True}, ...]
        :return: ID of the created question.
        """
        question_id = self._add(Question(subject_id=subject_id, text=question_text))

        # Adding answers
        for answer in answers:
            self.add_answer(question_id=question_id, text=answer['text'], is_correct=answer['is_correct'])

        return question_id

    def get_questions(self, subject_id: int) -> List[Question]:
        with Session(self.engine) as session:
            statement = select(Question).where(Question.subject_id == subject_id)
            result = session.exec(statement)
            return result.all()

    def add_answer(self, question_id: int, text: str, is_correct: bool):
        return self._add(Answer(question_id=question_id, text=text, is_correct=is_correct))

    def add_result(self, user_id: int, test_id: str, subject_id: int, question_ids: str):
        return self._add(Result(user_id=user_id, test_id=test_id, subject_id=subject_id, question_ids=question_ids))

    def check_reslt(self, user_id: int, status: bool):
        with Session(self.engine) as session:
            statement = select(Result).where(Result.user_id == user_id, Result.status == status)
            result = session.exec(statement)
            return result.all()

    def add_test(self, user_id: int, test_id: str, subject_id: int, question_id: int):
        return self._add(Test(user_id=user_id, test_id=test_id, subject_id=subject_id, question_id=question_id))




