import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import DATABASES
from app.config.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DATABASES['test']['ENGINE'], connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()

    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as client:
        yield client
