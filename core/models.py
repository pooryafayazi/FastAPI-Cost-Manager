# core/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from db import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)

    def __repr__(self):
        return f"Expense(id={self.id}, description={self.description}, amount={self.amount})"

