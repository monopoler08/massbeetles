# content of tests/conftest.py
import pytest
from models.base import Base


@pytest.fixture
def db_session():
    Base.metadata.create_all(engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
