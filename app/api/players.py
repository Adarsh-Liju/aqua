from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db import get_session
from app.models import PlayerScores, Players, Quizzes, Users

router = APIRouter()
templates = Jinja2Templates(directory="templates")
SessionDep = Annotated[Session, Depends(get_session)]


def _current_user(request: Request, session: Session) -> Users | None:
    raw = request.cookies.get("user_id")
    if not raw:
        return None
    try:
        return session.get(Users, int(raw))
    except (ValueError, TypeError):
        return None


@router.get("/players/setup")
async def players_setup_page(request: Request, session: SessionDep):
    user = _current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "players_setup.html", {"user": user})


@router.post("/players/setup")
async def create_players(request: Request, session: SessionDep):
    user = _current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()
    names = [v.strip() for v in form.getlist("player_name") if str(v).strip()]

    if not (2 <= len(names) <= 8):
        return templates.TemplateResponse(
            request, "players_setup.html",
            {"user": user, "error": "Please enter between 2 and 8 player names."},
            status_code=400,
        )

    # Remove previous players for this user before creating fresh ones
    old_players = session.scalars(select(Players).where(Players.user_id == user.id)).all()
    for p in old_players:
        old_scores = session.scalars(
            select(PlayerScores).where(PlayerScores.player_id == p.id)
        ).all()
        for s in old_scores:
            session.delete(s)
        session.delete(p)
    session.commit()

    for order, name in enumerate(names, start=1):
        session.add(Players(user_id=user.id, name=name, turn_order=order))
    session.commit()

    return RedirectResponse(url="/players", status_code=303)


@router.get("/players")
async def players_page(request: Request, session: SessionDep):
    user = _current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    players = session.scalars(
        select(Players).where(Players.user_id == user.id).order_by(Players.turn_order)
    ).all()

    quizzes = session.scalars(select(Quizzes)).all()

    # Build per-player score data
    player_data = []
    for p in players:
        scores = session.scalars(
            select(PlayerScores).where(PlayerScores.player_id == p.id)
        ).all()
        received = session.scalars(
            select(PlayerScores).where(PlayerScores.passed_to_player_id == p.id)
        ).all()
        own_total = sum(s.score for s in scores if s.passed_to_player_id is None)
        received_total = sum(s.score for s in received)
        player_data.append({
            "player": p,
            "scores": scores,
            "own_total": own_total,
            "received_total": received_total,
            "effective_total": own_total + received_total,
        })

    return templates.TemplateResponse(
        request, "players_scores.html",
        {"user": user, "player_data": player_data, "players": players, "quizzes": quizzes},
    )


@router.post("/players/{player_id}/score")
async def record_score(
    request: Request,
    player_id: int,
    session: SessionDep,
    quiz_id: int = Form(...),
    score: int = Form(...),
    total_questions: int = Form(...),
):
    user = _current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    player = session.get(Players, player_id)
    if not player or player.user_id != user.id:
        return RedirectResponse(url="/players", status_code=303)

    session.add(PlayerScores(
        player_id=player_id,
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
    ))
    session.commit()
    return RedirectResponse(url="/players", status_code=303)


@router.post("/players/{player_id}/pass")
async def pass_score(
    request: Request,
    player_id: int,
    session: SessionDep,
    score_id: int = Form(...),
    to_player_id: int = Form(...),
):
    user = _current_user(request, session)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    player = session.get(Players, player_id)
    target = session.get(Players, to_player_id)
    if not player or player.user_id != user.id:
        return RedirectResponse(url="/players", status_code=303)
    if not target or target.user_id != user.id or target.id == player_id:
        return RedirectResponse(url="/players", status_code=303)

    ps = session.get(PlayerScores, score_id)
    if not ps or ps.player_id != player_id or ps.passed_to_player_id is not None:
        return RedirectResponse(url="/players", status_code=303)

    ps.passed_to_player_id = to_player_id
    session.add(ps)
    session.commit()
    return RedirectResponse(url="/players", status_code=303)
