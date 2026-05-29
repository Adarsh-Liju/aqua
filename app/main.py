from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database.db import create_db
from app.database.seed import seed_quiz

seed_quiz()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP RUNNING")
    create_db()

    yield

    print("Shutting down...")


app = FastAPI(
    title="AI Quiz Generator",
    lifespan=lifespan
)