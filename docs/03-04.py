# main.py
from fastapi import FastAPI


app = FastAPI()

name_list = [
    {"id": 1, "name": "ali"},
    {"id": 2, "name": "rose"},
    {"id": 3, "name": "pedram"},
    {"id": 4, "name": "aziz"},
    {"id": 5, "name": "zahra"},
]


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.get("/names")
def retieve_name_list():
    return name_list

# so now can access name list in 127.0.0.1:8000/names


# path :
# /names (GET(RETRIEVE),POST(CREATE))

# /names/:id (GET(RETRIEVE),PUT/PATCH(UPDATE),DELETE)
