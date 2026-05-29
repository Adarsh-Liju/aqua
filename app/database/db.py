from sqlmodel import Session, SQLModel, create_engine
from app import models  # noqa: F401 — registers models in metadata
from app.config import settings

engine = create_engine(settings.database_url, echo=settings.db_echo)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session