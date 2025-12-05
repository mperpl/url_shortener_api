from fastapi import Request
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import UrlMapping

SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_testing_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_db():
   yield from create_db_testing_session()
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def session(clean_db):
    yield from create_db_testing_session()


@pytest.fixture
def client():
    test_client = TestClient(app)
    yield test_client


@pytest.fixture()
def clean_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def dummy_data(session):
    dummy_mapping1 = UrlMapping(url='https://www.youtube.com', short_code=1, clicks=99)
    dummy_mapping2 = UrlMapping(url='https://www.google.com', short_code=2, clicks=99)

    session.add(dummy_mapping1)
    session.add(dummy_mapping2)

    session.commit()

    session.refresh(dummy_mapping1)
    session.refresh(dummy_mapping2)

    
