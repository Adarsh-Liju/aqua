from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel


class Quizzes(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    topic: str
    questions: list["Questions"] = Relationship(back_populates="quiz")


class Questions(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quizzes.id")
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    quiz: "Quizzes" = Relationship(back_populates="questions")


class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str = Field(unique=True)


class QuizAttempts(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    quiz_id: int = Field(foreign_key="quizzes.id")
    score: int
    total_questions: int
    started_at: datetime
    completed_at: datetime
    quiz: "Quizzes" = Relationship()
    user: "Users" = Relationship()


class Answers(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="quizattempts.id")
    question_id: int = Field(foreign_key="questions.id")
    selected_option: str
    is_correct: bool
