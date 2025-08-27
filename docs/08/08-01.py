# +++++++++++++ با uv +++++++++++++
# نصب پایتون و ساخت محیط (در صورت نبود)
# uv python install 3.12
# uv venv

# ایجاد pyproject و افزودن وابستگی
# uv init
# uv add fastapi uvicorn sqlalchemy

# اجرای اسکریپت/اپ در venv
# uv run uvicorn app.main:app --reload

# قفل نسخه‌ها و نصب دقیق
# uv lock
# uv sync


# +++++++++++++ با Poetry +++++++++++++
# ایجاد پروژه
# poetry new myapp
# cd myapp

# تنظیم پایتون هدف
# poetry env use 3.12

# افزودن وابستگی
# poetry add fastapi uvicorn sqlalchemy

# اجرای اپ در محیط Poetry
# poetry run uvicorn app.main:app --reload

# قفل/نصب
# poetry lock
# poetry install

# ساخت بسته و انتشار (در صورت نیاز)
# poetry build
# poetry publish


# الگوی فایل‌ها
# pyproject.toml نمونه (مشترک برای uv یا Poetry)
"""
[project]
name = "fastapi-service"
version = "0.1.0"
description = "A FastAPI-based service"
requires-python = ">=3.11"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "sqlalchemy",
  "pydantic>=2",
]

[tool.uv]               # اگر uv استفاده کنی
dev-dependencies = ["pytest", "httpx", "ruff"]

[tool.poetry]          # اگر Poetry استفاده کنی
authors = ["You <you@example.com>"]

[tool.poetry.dependencies]
python = ">=3.11"
fastapi = "*"
uvicorn = {extras = ["standard"]}
sqlalchemy = "*"
pydantic = "^2"

[tool.poetry.group.dev.dependencies]
pytest = "*"
httpx = "*"
ruff = "*"

"""


# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# مهاجرت سریع از requirements.txt

# به uv:
'''
uv init
uv add -r requirements.txt
uv lock && uv sync
'''

# به Poetry:
'''
poetry init    # و پاسخ‌دهی به پرسش‌ها
poetry add $(cat requirements.txt)
poetry lock && poetry install
'''

