import json
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database.db import create_db, get_session
from app.database.seed import seed_quiz
from app.models import Questions, Quizzes, Users


templates = Jinja2Templates(directory="templates")
SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    seed_quiz()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"name": "Adarsh"})


@app.get("/quiz")
async def quiz(request: Request, session: SessionDep, quiz_id: int | None = None):
    if quiz_id is not None:
        quiz_obj = session.get(Quizzes, quiz_id)
    else:
        quiz_obj = session.exec(select(Quizzes)).first()

    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = session.exec(
        select(Questions).where(Questions.quiz_id == quiz_obj.id)
    ).all()

    questions_json = json.dumps([
        {
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "correct_option": q.correct_option,
        }
        for q in questions
    ])

    return templates.TemplateResponse(
        request, "quiz.html", {
            "quiz": quiz_obj,
            "questions_count": len(questions),
            "questions_json": questions_json,
        }
    )


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"error": None})


@app.post("/register")
async def register_user(
    request: Request,
    session: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
):
    existing = session.exec(
        select(Users).where(Users.email == email)
    ).first()
    if existing:
        return templates.TemplateResponse(
            request, "register.html",
            {"error": "An account with that email already exists."},
            status_code=400,
        )

    user = Users(username=username, email=email)
    session.add(user)
    session.commit()

    return RedirectResponse(url="/quiz", status_code=303)
