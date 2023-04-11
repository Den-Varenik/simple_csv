from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.settings import DATABASES

engine = create_engine(DATABASES['default']['ENGINE'])
Session = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.rollback()
        db.close()
