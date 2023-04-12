from datetime import date
from typing import List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base, get_db
from app.config.settings import DATABASES
from app.main import app
from app.models.categories import Category
from app.models.users import User


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


@pytest.fixture(scope="function")
def users(db) -> List[User]:
    # Create test data
    user1 = User(
        firstname="Alice",
        lastname="Smith",
        email="alice@example.com",
        gender="female",
        birthDate=date(1990, 1, 1)
    )
    user2 = User(
        firstname="Bob",
        lastname="Jones",
        email="bob@example.com",
        gender="male",
        birthDate=date(1985, 1, 1)
    )
    user3 = User(
        firstname="Charlie",
        lastname="Brown",
        email="charlie@example.com",
        gender="male",
        birthDate=date(2000, 1, 1)
    )
    category1 = Category(name="Toys")
    category2 = Category(name="Electronics")
    user1.categories.append(category1)
    user2.categories.append(category2)
    user3.categories.extend([category1, category2])
    db.add_all([user1, user2, user3])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    db.refresh(user3)
    return [user1, user2, user3]
