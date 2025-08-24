from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
# SQLALCHEMY_DATABASE_URL = "sqlite:///./:memory:"

# for postgres or other relationsal databases
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host:5432/database_name"
# SQLALCHEMY_DATABASE_URL = "mysql://username:possword@localhost/db_name"


# Example for a SQLite database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False # only sqlite
                  }
    )

# sessionmake as cursor 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create base class for declaring tables
Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True, )
    description = Column(String(30))
    amount = Column(Integer)

    def __repr__(self):
        return f"User (id = {self.id} , description = {self.description} , amount = {self.amount})"

# to create tables and database
Base.metadata.create_all(engine)

session = SessionLocal()


# inserting data
"""
first_loan = Expense(description="car loan", amount="155000")
session.add(first_loan)
session.commit()
"""

# bulk insert
"""
car_rent = Expense(description="car rent", amount="155000")
home_loan = Expense(description="home loan", amount="185000")
machine_car = Expense(description="machine car", amount="3540")
list_of_add = [car_rent, home_loan, machine_car]
session.add_all(list_of_add)
session.commit()
"""

# retrieve all data
"""
expenses = session.query(Expense).all()
print(expenses)
[print(e) for e in expenses]
"""


# retrieve a data with filter in equality base
"""
expenses = session.query(Expense).filter_by(description = "car loan", amount=155000).all()
[print(e) for e in expenses]
"""


# see query command, without .all()
"""
expenses = session.query(Expense).filter_by(description = "car loan", amount=155000)
print(expenses)
"""


# first
"""
expenses = session.query(Expense).filter_by(description = "car loan", amount=155000).first()
print(expenses)
"""


# one_or_none if there is no more than one
"""
expenses = session.query(Expense).filter_by(description = "car loan", amount=155000).one_or_none()
print(expenses)

expense = session.query(Expense).filter_by(id = 6).first()
print(expense)

# delete
if expense:
    session.delete(expense)
    session.commit()

# edit and updates
expense.description = "sixth loan"
expense.amount = 242020
session.commit()
"""


"""
expenses_all = session.query(Expense).all()

# query all expenses with amount greater than or equal to 25
expenses_filtered = session.query(Expense).filter(Expense.amount >= 25).all()

print("ALL Expenses: ", len(expenses_all))
print("Filtered Expenses: ", len(expenses_filtered))

# add multiple filters
# query all expenses with amount greater than or equal to 25 and description equals to something
expenses_filtered = session.query(Expense).filter(Expense.amount >= 25, Expense.description == "loan").all()

# or you can use where
expenses_filtered = session.query(Expense).where(Expense.amount >= 25, Expense.description == "loan").all()

# expenses with similar description containing specific substrings
expenses_similar_description = session.query(Expense).filter(Expense.description.like("%car%")).all()

# expenses with case insensitive match
expenses_similar_description = session.query(Expense).filter(Expense.description.ilike("%car%")).all()

# expenses with starting and ending chars
expenses_starting_car = session.query(Expense).filter(Expense.description.like("Car%")).all()
expenses_endingc_car = session.query(Expense).filter(Expense.description.like("%Car")).all()
"""



"""
from sqlalchemy import or_, and_, not_

# query those who has car as description or amount above 25
expenses_filtered = session.query(Expense).filter(or_(Expense.amount >= 25, Expense.description == "car")).all()

# query those who has loan as description and amount above 25
expenses_filtered = session.query(Expense).filter(and_(Expense.amount >= 25, Expense.description == "loan")).all()

# query those whose description is not car
expenses_filtered = session.query(Expense).filter(not_(Expense.description == "car")).all()

# getting expenses which are not description car or amount between 35,60
expenses = session.query(Expense).filter(or_(not_(Expense.description == "car"), and_(Expense.amount > 35000, Expense.amount < 600000))).all()
"""



"""
from sqlalchemy import func
# 1. Count Total Expenses
total_users = session.query(func.count(Expense.id)).scalar()
print("Total Expenses:", total_users)

# 2. Find the Average Age of Expenses
average_amount = session.query(func.avg(Expense.amount)).scalar()
print("Average Age:", average_amount)

# 3. Find the Maximum and Minimum Age
max_amount = session.query(func.max(Expense.amount)).scalar()
min_amount = session.query(func.min(Expense.amount)).scalar()
print(f"Max Age: {max_amount}, Min Age: {min_amount}")
"""



"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))   # رابطه با جدول کاربران
    total_amount = Column(Float, nullable=False)        # مبلغ سفارش
    created_date = Column(DateTime, default=datetime.now())  # تاریخ ایجاد سفارش

    # رابطه برعکس با Expense
    expense = relationship("Expense", back_populates="orders")

# 4. Find the Total Number of Orders
total_orders = session.query(func.count(Order.id)).scalar()
print("Total Orders:", total_orders)

# 5. Find the Sum of All Order Amounts
total_revenue = session.query(func.sum(Order.total_amount)).scalar()
print("Total Revenue:", total_revenue)

# 6. Find the Average Order Value
average_order_value = session.query(func.avg(Order.total_amount)).scalar()
print("Average Order Value:", average_order_value)

# 7. Find Expenses Who Have Placed the Most Orders
most_active_expenses = (session.query(Expense.description, func.count(Order.id).label("order_count")
                                      ).join(Order).group_by(Expense.id).order_by(func.count(Order.id).desc()).limit(5).all())
print("Top 5 Active Expenses by Order Count:", most_active_expenses)

# 8. Find Expenses with the Highest Total Spending
top_spenders = (session.query(Expense.description, func.sum(Order.total_amount).label("total_spent")
                              ).join(Order).group_by(Expense.id).order_by(func.sum(Order.total_amount).desc()).limit(5).all())
print("Top 5 Expenses by Spending:", top_spenders)

# 9. Find Expenses Who Have Not Placed Any Orders
expenses_without_orders = (session.query(Expense).outerjoin(Order).filter(Order.id == None).all())
print("Expenses Without Orders:", [expense.description for expense in expenses_without_orders])

# 10. Find the Most Recent Order Date
latest_order_date = session.query(func.max(Order.created_date)).scalar()
print("Most Recent Order Date:", latest_order_date)


# Close the session
session.close()
"""



"""
from sqlalchemy.sql import text

# Example 1: Count Expenses with a Specific Condition (Raw SQL)
query = text("SELECT COUNT(*) FROM expense WHERE amount >= :min_amount")
result = session.execute(query, {"min_amount": 25}).scalar()
print("Expenses with amount >= 25:", result)


# Example 2: Find the Average amount of Expenses (Raw SQL)
query = text("SELECT AVG(amount) FROM expense")
result = session.execute(query).scalar()
print("Average amount of Expenses:", result)


# Example 3: Get Expenses with a Specific description (Raw SQL)
query = text("SELECT * FROM expense WHERE de = :description")
result = session.execute(query, {"description": "Car"}).fetchall()
print("Expenses named Car:", [expense.description for expense in result])


# Example 4: Aggregate Query for the Total Revenue (Raw SQL)
query = text("SELECT SUM(total_amount) FROM \"order\"")
result = session.execute(query).scalar()
print("Total Revenue:", result)
"""



"""
# 1. محاسبه تعداد هزینه ها برای هر کاربر
expenses_order_count = session.query(
    Expense.id, Expense.description, func.count(Order.id).label("order_count")
).join(Order).group_by(Expense.id).all()

for expense in expenses_order_count:
    print(f"Expense: {expense.description}, Order Count: {expense.order_count}")


# 2. محاسبه مجموع مبالغ هزینه ها هر کاربر
expense_total_spent = session.query(
    Expense.id, Expense.description, func.sum(Order.total_amount).label("total_spent")
).join(Order).group_by(Expense.id).all()

for expense in expense_total_spent:
    print(f"Expense: {expense.description}, Total Spent: {expense.total_spent}")
"""



"""
from enum import Enum as PythonEnum
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, Numeric,
    Date, DateTime, Time, Interval, Enum, ForeignKey, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON
from sqlalchemy.orm import relationship


class RelationsTable(Base):
    __tablename__ = "users"

    # One-to-one relationship
    profile = relationship("Profile", uselist=False, back_populates="user")

    # One-to-many relationship
    addresses = relationship("Address", back_populates="user")

    # Many-to-one relationship
    orders = relationship("Order", back_populates="user")

    # Many-to-many relationship
    roles = relationship("Role", secondary="user_roles",
                         back_populates="users")
    

class UserType(PythonEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class SampleModel(Base):
    __tablename__ = "sample_model"

    id = Column(Integer, primary_key=True)
    uuid_field = Column(UUID)

    string_field = Column(String(100))
    text_field = Column(Text)
    boolean_field = Column(Boolean)
    integer_field = Column(Integer)
    float_field = Column(Float)
    numeric_field = Column(Numeric(10, 2))
    date_field = Column(Date)
    datetime_field = Column(DateTime)
    time_field = Column(Time)
    interval_field = Column(Interval)
    enum_field = Column(Enum(UserType))
    array_field = Column(ARRAY(Integer))
    json_field = Column(JSON)
    foreign_key_field = Column(Integer, ForeignKey('related_table.id'))
    binary_field = Column(LargeBinary)
"""



