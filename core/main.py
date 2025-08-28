# core/main.py
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
import time
import random
import httpx
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
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
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.interval import IntervalTrigger


# scheduler = AsyncIOScheduler()


# def my_task():
    # print(f"Task executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup")
    # scheduler.add_job(my_task, IntervalTrigger(seconds=10))
    # scheduler.start()
    
    yield
    
    # scheduler.shutdown()
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


# set up the cache backend
cache_backend = InMemoryBackend()
FastAPICache.init(cache_backend)


async def request_current_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        current_weather = data.get("current", {})
        return current_weather
    else:
        return None


@app.get("/fetch-current-weather", status_code=200)
@cache(expire=10)
async def fetch_current_weather(latitude: float = 40.7128, longitude: float = -74.0060):
    current_weather = await request_current_weather(latitude, longitude)

    if current_weather:
        return JSONResponse(content={"current_weather": current_weather})
    else:
        return JSONResponse(content={"detail": "Failed to fetch weather"}, status_code=500)


@app.get("/fetch-current-weather-manually-and-without-header", status_code=200)
async def fetch_current_weather(latitude: float = 40.7128, longitude: float = -74.0060):
    cache_key = f"weather-{latitude}-{longitude}"

    cached_data = await cache_backend.get(cache_key)
    if cached_data:
        return JSONResponse(content={"current_weather": cached_data})

    current_weather = await request_current_weather(latitude, longitude)

    if current_weather:
        await cache_backend.set(cache_key, str(current_weather), 10)
        return JSONResponse(content={"current_weather": current_weather})
    else:
        return JSONResponse(content={"detail": "Failed to fetch weather"}, status_code=500)
