# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.orm import sessionmaker, declarative_base

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"
# SQLALCHEMY_DATABASE_URL = "sqlite:///./:memory:"

# for postgres or other relationsal databases
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host:5432/database_name"
# SQLALCHEMY_DATABASE_URL = "mysql://username:possword@localhost/db_name"


# Example for a SQLite database
# engine = create_engine(
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # only sqlite
# )

# sessionmake as cursor
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create base class for declaring tables
# Base = declarative_base()


"""
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
"""

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

"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30))
    email = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # addresses = relationship("Address", back_populates="user")
    addresses = relationship("Address", backref="user")

    # رابطه One-to-One با Profile
    profile = relationship("Profile", backref="user", uselist=False)

    posts = relationship("Post", backref="user")
    courses = relationship(
        "Course", secondary="enrollments", back_populates="attendess"
    )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)

    # user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id}, user_id={self.user_id}, city={self.city}, state={self.state}, zip_code={self.zip_code})"
"""

# Base.metadata.create_all(engine)

# session = SessionLocal()

# --- افزودن یک کاربر جدید ---
# session.add(User(username="pooryafayazi", email="poorya152@gmail.com", password="123"))
# session.commit()

# گرفتن یوزر
# user = session.query(User).filter_by(username="pooryafayazi").one_or_none()

# --- افزودن آدرس‌ها به کاربر ---
# addresses = [
# Address(user_id=user.id, city="karaj", state="alborz", zip_code="123"),
# Address(user_id=user.id, city="tehran", state="tehran", zip_code="123")
# ]
# session.add_all(addresses)
# session.commit()

# دسترسی به آدرس‌ها از طریق رابطه
# print(user.addresses)

# گرفتن آدرس خاص
# address = session.query(Address).filter_by(user_id=user.id, city="karaj").one_or_none()
# print(address.user.username)

"""
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String)
    last_name = Column(String)
    bio = Column(Text, nullable=True)

    def __repr__(self):
        return f"Profile(id={self.id}, first_name={self.first_name}, last_name={self.last_name})"
"""

# Base.metadata.create_all(engine)

# session = SessionLocal()


# گرفتن یک کاربر
# user = session.query(User).filter_by(username="pooryafayazi").one_or_none()

# اگر کاربر وجود داشت، می‌تونیم پروفایل براش بسازیم
# session.add(Profile(user_id=user.id, first_name="Poorya", last_name="Fayazi", bio="Developer"))
# session.commit()

# print(user.profile.first_name)

"""
from sqlalchemy import DateTime
from datetime import datetime


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # ارتباط با جدول users
    title = Column(String)
    content = Column(Text)

    created_date = Column(DateTime, default=datetime.now)
    # or
    # from sqlalchemy.sql import func
    # created_date = Column(DateTime, default=func.now())
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    comments = relationship("Comment", backref="post")

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title})"


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(
        Integer, ForeignKey("comments.id"), nullable=True
    )  # برای ریپلای به کامنت دیگر

    content = Column(Text)
    created_date = Column(DateTime, default=datetime.now)

    # روابط
    # parent = relationship("Comment", back_populates="children", remote_side=[id])
    # children = relationship("Comment", back_populates="parent", remote_side=[parent_id])

    # or
    from sqlalchemy.orm import backref

    children = relationship("Comment", backref=backref("parent", remote_side=[id]))

    def __repr__(self):
        return f"Comment(id={self.id}, post_id={self.post_id}, user_id={self.user_id} parent id = {self.parent_id})"
"""


# Base.metadata.create_all(engine)

# session = SessionLocal()


# user = session.query(User).filter_by(username="pooryafayazi").one_or_none()

# ساخت یک پست جدید برای کاربر
# session.add(Post(user_id=user.id, title="example", content="post content"))
# session.commit()


# گرفتن اولین پست کاربر
# post = user.posts[0]

# اضافه کردن یک کامنت به همون پست
# session.add(Comment(user_id=user.id, post_id=post.id, content="this is a parent comment"))
# session.commit()

# parent_comment = post.comments[0]
# print(parent_comment)

# session.add(Comment(user_id=user.id, post_id=post.id, parent_id=parent_comment.id, content="this is a replay 2 comment"))
# session.commit()


# print(post.comments)


# comments = session.query(Comment).filter_by(post_id=post.id, parent_id=None).all()
# print(comments)


# comments = session.query(Comment).filter_by(post_id=post.id, parent_id=None).all()
# [print(comment) for comment in comments]
# [print(comment.children) for comment in comments]

"""
from sqlalchemy import Table, UniqueConstraint


enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("enrolled_date", DateTime, default=datetime.now),
    UniqueConstraint("user_id", "course_id", name="uniqque_user_course_enrolled"),
)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    description = Column(Text)

    created_date = Column(DateTime, default=datetime.now)

    # رابطه Many-to-Many با User
    attendess = relationship("User", secondary=enrollments, back_populates="courses")

    def __repr__(self):
        return f"Course(id={self.id}, title={self.title})"
"""

# Base.metadata.create_all(engine)

# session = SessionLocal()

# user = session.query(User).filter_by(username="pooryafayazi").one_or_none()


# اضافه کردن یک دوره جدید
# session.add(Course(title="Python", description="this is a python course"))
# session.commit()


# پیدا کردن دوره
# course = session.query(Course).filter_by(title="Python").one()

# اضافه کردن کاربر به دوره
# course.attendess.append(user)   # چون در مدل Course اسم رابطه رو users گذاشتیم
# session.commit()


# print(course.attendess)
# print(user.courses)
