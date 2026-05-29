import json
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database.db import get_session
from app.models import Players, Questions, Quizzes

router = APIRouter()
templates = Jinja2Templates(directory="templates")
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/quiz")
async def quiz(request: Request, session: SessionDep, quiz_id: int | None = None, player_id: int | None = None):
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

    players_json = "null"

    def _players_to_json(player_list):
        return json.dumps([
            {"id": p.id, "name": p.name, "turn_order": p.turn_order}
            for p in player_list
        ])

    if player_id is not None:
        current_player = session.get(Players, player_id)
        if current_player:
            session_players = session.exec(
                select(Players)
                .where(Players.user_id == current_player.user_id)
                .order_by(Players.turn_order)
            ).all()
            players_json = _players_to_json(session_players)
    else:
        # No player_id given — load players from the session cookie and default to player 1
        raw_uid = request.cookies.get("user_id")
        if raw_uid:
            try:
                uid = int(raw_uid)
                session_players = session.exec(
                    select(Players)
                    .where(Players.user_id == uid)
                    .order_by(Players.turn_order)
                ).all()
                if session_players:
                    players_json = _players_to_json(session_players)
                    player_id = session_players[0].id
            except (ValueError, TypeError):
                pass

    return templates.TemplateResponse(
        request, "quiz.html", {
            "quiz": quiz_obj,
            "questions_count": len(questions),
            "questions_json": questions_json,
            "player_id": player_id,
            "players_json": players_json,
        }
    )


@router.get("/quiz/generate")
async def quiz_generate_page(request: Request, player_id: int | None = None):
    return templates.TemplateResponse(
        request, "quiz_generate.html", {"player_id": player_id}
    )


@router.post("/quiz/generate")
async def quiz_generate_create(
    request: Request,
    session: SessionDep,
    topic: str = Form(...),
    questions_json: str = Form(...),
    player_id: int | None = Form(default=None),
):
    try:
        raw = json.loads(questions_json)
    except json.JSONDecodeError:
        return templates.TemplateResponse(
            request, "quiz_generate.html",
            {"player_id": player_id, "error": "Invalid JSON — make sure you paste the raw JSON array from Claude."},
            status_code=400,
        )

    if not isinstance(raw, list) or len(raw) == 0:
        return templates.TemplateResponse(
            request, "quiz_generate.html",
            {"player_id": player_id, "error": "Expected a JSON array of questions."},
            status_code=400,
        )

    required = {"question_text", "option_a", "option_b", "option_c", "option_d", "correct_option"}
    if not all(required.issubset(q.keys()) for q in raw):
        return templates.TemplateResponse(
            request, "quiz_generate.html",
            {"player_id": player_id, "error": "One or more questions are missing required fields."},
            status_code=400,
        )

    quiz_obj = Quizzes(title=f"{topic} Quiz", topic=topic)
    session.add(quiz_obj)
    session.commit()
    session.refresh(quiz_obj)

    for q in raw:
        correct = str(q["correct_option"]).upper()
        if correct not in ("A", "B", "C", "D"):
            correct = "A"
        session.add(Questions(
            quiz_id=quiz_obj.id,
            question_text=str(q["question_text"]),
            option_a=str(q["option_a"]),
            option_b=str(q["option_b"]),
            option_c=str(q["option_c"]),
            option_d=str(q["option_d"]),
            correct_option=correct,
        ))
    session.commit()

    url = f"/quiz?quiz_id={quiz_obj.id}"
    if player_id:
        url += f"&player_id={player_id}"
    return RedirectResponse(url=url, status_code=303)
