# core/tests/conftest.py
import os


os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("COOKIE_SAMESITE", "lax")
os.environ.setdefault("COOKIE_SECURE", "False")


from fastapi.testclient import TestClient
import pytest
from faker import Faker
from main import app
from core.db import Base, get_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine    
from users.models import UserModel
from expenses.models import ExpenseModel


faker = Faker()


SQLALCHEMY_DATABASE_URL = "sqlite://"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
    )

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Each test: an isolated session with rollback transaction
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def app_with_overrides(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield app
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def anon_client(app_with_overrides):
    return TestClient(app_with_overrides)


@pytest.fixture(scope="function")
def user_factory(db_session):
    def _make_user(username="user", password="pass", **kwargs):
        user = UserModel(username=username, **kwargs)
        if hasattr(user, "set_password") and callable(user.set_password):
            user.set_password(password)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _make_user


# loggined client with cookie
@pytest.fixture(scope="function")
def auth_client(anon_client, user_factory):
    user_factory(username="usertest", password="12345678")
    resp = anon_client.post(
        "/api/v1/users/login-cookie",
        json={"username": "usertest", "password": "12345678"},
    )
    assert resp.status_code == 200
    return anon_client


# endpoint with CSRF
import secrets
@pytest.fixture(scope="function")
def auth_client_with_csrf(auth_client):
    csrf = secrets.token_urlsafe(16)
    auth_client.cookies.set("csrf_token", csrf, path="/")
    auth_client.headers.update({"x-csrf-token": csrf})
    return auth_client


@pytest.fixture(scope="function")
def expense_factory(db_session):
    """
    expense_factory(user_id=123, n=3)
    expense_factory(username="usertest", n=5)
    """
    def _make_expenses(*, user_id: int | None = None, username: str | None = None, n: int = 3):
        if user_id is None:
            if username is None:
                username = "usertest"
            user_id = db_session.query(UserModel.id)\
                                .filter(UserModel.username == username)\
                                .scalar()
            assert user_id is not None, "User for expense_factory not found"

        items = []
        for i in range(n):
            items.append(
                ExpenseModel(
                    user_id=user_id,
                    description=f"expense {i+1}",
                    amount=100 + i,
                )
            )
        db_session.add_all(items)
        db_session.commit()
        return items
    return _make_expenses
