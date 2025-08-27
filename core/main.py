# core/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from expenses.routs import router as expenses_router
from users.routs import router as users_router
from i18n.i18n import I18n, get_translator

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup")
    yield
    print("Application Shutdown")


tags_metadata = [{"name": "expenses", "descriptions": "Operations related to expense management", "externalDocs": {"description": "More about expenses", "url": "http://127.0.0.1:8000/docs/expenses"}}]


app = FastAPI(
    title="ToDo-App",
    description="This is a Cost Manager app",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Poorya Fayazi",
        "url": "https://itmeter.ir/about",
        "email": "poorya189@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.include_router(expenses_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


# +++++++++++ JWT +++++++++++
from fastapi.security import HTTPBearer
from fastapi import Depends
from auth.jwt_auth import get_authenticated_user

security = HTTPBearer()


@app.get("/public",)
def public_rout():
    return {"detail": "this is public rout"}


@app.get("/private",)
def private_rout(user=Depends(get_authenticated_user)):
    return {"detail": "this is public rout", "username": user.username}

@app.get("/hello")
def hello(tr: I18n = Depends(get_translator)):
    return {"message": tr("common.hello", name="Poorya")}