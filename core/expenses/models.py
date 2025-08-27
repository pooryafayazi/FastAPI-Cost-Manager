# core/expenses/models.py
from sqlalchemy import Column, Integer, String, func, DateTime, ForeignKey
from core.db import Base
from sqlalchemy.orm import relationship


class ExpenseModel(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    description = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)

    create_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user = relationship("UserModel", back_populates="expenses", uselist=False)

    def __repr__(self):
        return f"Expense(id={self.id}, description={self.description}, amount={self.amount})"

