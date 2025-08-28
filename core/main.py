# core/main.py
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
import time
import random
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import HTTPBearer
from fastapi import FastAPI, Depends, Request, BackgroundTasks
from auth.jwt_auth import get_authenticated_user
from expenses.routs import router as expenses_router
from users.routs import router as users_router
from i18n.i18n import I18n, get_translator
from exceptions import (
    AppError, 
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup")
    yield
    print("Application Shutdown")


tags_metadata = [
    {
        "name": "expenses",
        "descriptions": "Operations related to expense management",
        "externalDocs": {
            "description": "More about expenses",
            "url": "http://127.0.0.1:8000/docs/expenses",
        },
    }
]


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

security = HTTPBearer()


@app.get("/public")
def public_rout():
    return {"detail": "this is public rout"}


@app.get("/private")
def private_rout(user=Depends(get_authenticated_user)):
    return {"detail": "this is public rout", "username": user.username}


@app.get("/hello")
def hello(tr: I18n = Depends(get_translator)):
    return {"message": tr("common.hello", name="Poorya")}


app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    # print("before")
    response = await call_next(request)
    # print("after")
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


task_counter = 1

def start_task(task_id: int):
    print(f"doing the process: {task_id}")
    time.sleep(random.randint(3, 10))
    print(f"finished task {task_id}")

@app.get("/initiate-task", status_code=200)
async def initiate_task(background_tasks: BackgroundTasks):
    global task_counter
    background_tasks.add_task(start_task, task_id=task_counter)
    task_counter += 1
    return JSONResponse(content={"detail": "task is done"})