from sqlmodel import Session
from sqlmodel import SQLModel
from sqlmodel import create_engine
from app import models

DATABASE_URL = (
    "mysql+pymysql://adarsh:ala@localhost/aqua"
)

engine = create_engine(
    DATABASE_URL,
    echo=True
)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session