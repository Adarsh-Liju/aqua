from sqlmodel import Session, select

from app.database.db import engine
from app.models import Quizzes, Questions


def seed_quiz():
    with Session(engine) as session:

        existing = session.exec(
            select(Quizzes).where(
                Quizzes.title == "Indian Polity Basics"
            )
        ).first()

        if existing:
            print("Quiz already exists")
            return

        quiz = Quizzes(
            title="Indian Polity Basics",
            topic="Indian Polity",
        )

        session.add(quiz)
        session.commit()
        session.refresh(quiz)

        questions = [
            Questions(
                quiz_id=quiz.id,
                question_text="Who is known as the Father of the Indian Constitution?",
                option_a="Mahatma Gandhi",
                option_b="Jawaharlal Nehru",
                option_c="B. R. Ambedkar",
                option_d="Sardar Patel",
                correct_option="C",
            ),
            Questions(
                quiz_id=quiz.id,
                question_text="How many Fundamental Rights are currently provided in India?",
                option_a="5",
                option_b="6",
                option_c="7",
                option_d="8",
                correct_option="B",
            ),
            Questions(
                quiz_id=quiz.id,
                question_text="Which article guarantees equality before law?",
                option_a="Article 14",
                option_b="Article 19",
                option_c="Article 21",
                option_d="Article 32",
                correct_option="A",
            ),
        ]

        session.add_all(questions)

        session.commit()

        print("Quiz seeded successfully")