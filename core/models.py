# core/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from db import engine, SessionLocal


Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)

    def __repr__(self):
        return f"Expense(id={self.id}, description={self.description}, amount={self.amount})"


# to create tables and database
Base.metadata.create_all(engine)

session = SessionLocal()

