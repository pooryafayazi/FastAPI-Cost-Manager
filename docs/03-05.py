# main.py
from fastapi import FastAPI


app = FastAPI()

names_list = [
    {"id": 1, "name": "ali"},
    {"id": 2, "name": "rose"},
    {"id": 3, "name": "pedram"},
    {"id": 4, "name": "aziz"},
    {"id": 5, "name": "zahra"},
]


@app.get("/")
def root():
    return {"message": "Hello World!"}

# /names (GET(RETRIEVE),POST(CREATE))


@app.get("/names")
def retieve_name_list():
    return names_list

# /names/:id (GET(RETRIEVE),PUT/PATCH(UPDATE),DELETE)


@app.get("/names/{name_id}")
def retrieve_name_detail(name_id: int):
    for name in names_list:
        if name["id"] == name_id:
            return name
    return {"detail": "object not found!"}