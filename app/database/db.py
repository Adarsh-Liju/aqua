from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base
from app.config import settings

engine = create_engine(settings.database_url, echo=settings.db_echo)


def create_db():
    Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
