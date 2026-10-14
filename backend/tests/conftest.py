import os
os.environ["DATABASE_URL"] = "sqlite:///./test_rateshield.sqlite3"
os.environ["DEMO_MODE"] = "true"
import pytest
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app, limiter
from app import models

@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    limiter.reset()
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
