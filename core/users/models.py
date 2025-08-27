# core/users/models.py
from sqlalchemy import Column, Integer, String, Boolean, func, DateTime, ForeignKey
from core.db import Base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    create_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    expenses = relationship("ExpenseModel", back_populates="user", cascade="all, delete-orphan")

    def hash_password(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)


class TokenModel(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    token = Column(String, nullable=False, unique=True)
    create_date = Column(DateTime, server_default=func.now())

    users = relationship("UserModel", uselist=False)

    expires_in = Column(Integer, default=3600)  # one hour

    def is_expired(self) -> bool:
        created = self.create_date
        if created is not None and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        expire_time = (created or datetime.now(timezone.utc)) + timedelta(seconds=self.expires_in or 0)
        return datetime.now(timezone.utc) > expire_time
