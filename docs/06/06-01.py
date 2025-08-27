# command in core>pip install alembic

# command in core>alembic init migrations

# chenghe "sqlalchemy.url" variable to
#          sqlalchemy.url = sqlite:///./sqlite.db
#          which is been in "SQLALCHEMY_DATABASE_URL" variable in db.py file

# change "target_metadata" variable in migrations\env.py file to 
#         target_metadata=Base.metadata (from db import Base)
# add "import models" in migrations\env.py file

