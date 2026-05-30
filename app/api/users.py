from typing import Annotated
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db import get_session
from app.models import Users

router = APIRouter()
templates = Jinja2Templates(directory="templates")
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"error": None})


@router.post("/register")
async def register_user(
    request: Request,
    session: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
):
    existing = session.scalars(select(Users).where(Users.email == email)).first()
    if existing:
        return templates.TemplateResponse(
            request, "register.html",
            {"error": "An account with that email already exists."},
            status_code=400,
        )

    user = Users(username=username, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)

    response = RedirectResponse(url="/players/setup", status_code=303)
    response.set_cookie("user_id", str(user.id), httponly=True)
    return response


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login")
async def login_user(
    request: Request,
    session: SessionDep,
    email: str = Form(...),
):
    user = session.scalars(select(Users).where(Users.email == email)).first()
    if not user:
        return templates.TemplateResponse(
            request, "login.html",
            {"error": "No account found with that email."},
            status_code=400,
        )

    response = RedirectResponse(url="/players/setup", status_code=303)
    response.set_cookie("user_id", str(user.id), httponly=True)
    return response
