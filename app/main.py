from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database.db import create_db
from app.database.seed import seed_quiz
from app.api import home, players, quiz, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    seed_quiz()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(home.router)
app.include_router(quiz.router)
app.include_router(users.router)
app.include_router(players.router)
