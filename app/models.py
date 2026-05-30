from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Quizzes(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    topic: Mapped[str] = mapped_column(String(255))
    questions: Mapped[list["Questions"]] = relationship(back_populates="quiz")


class Questions(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id"))
    question_text: Mapped[str] = mapped_column(String(255))
    option_a: Mapped[str] = mapped_column(String(255))
    option_b: Mapped[str] = mapped_column(String(255))
    option_c: Mapped[str] = mapped_column(String(255))
    option_d: Mapped[str] = mapped_column(String(255))
    correct_option: Mapped[str] = mapped_column(String(255))
    quiz: Mapped["Quizzes"] = relationship(back_populates="questions")


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)


class QuizAttempts(Base):
    __tablename__ = "quizattempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id"))
    score: Mapped[int] = mapped_column(Integer)
    total_questions: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[datetime] = mapped_column(DateTime)
    quiz: Mapped["Quizzes"] = relationship()
    user: Mapped["Users"] = relationship()


class Answers(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizattempts.id"))
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"))
    selected_option: Mapped[str] = mapped_column(String(255))
    is_correct: Mapped[bool] = mapped_column(Boolean)


class Players(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    turn_order: Mapped[int] = mapped_column(Integer)


class PlayerScores(Base):
    __tablename__ = "playerscores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"))
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quizzes.id"))
    score: Mapped[int] = mapped_column(Integer)
    total_questions: Mapped[int] = mapped_column(Integer)
    passed_to_player_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("players.id"), nullable=True, default=None)
