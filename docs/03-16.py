# main.py
from fastapi import FastAPI


app = FastAPI()

names_list = [
    {"id": 1, "name": "ali"},
    {"id": 2, "name": "rose"},
    {"id": 3, "name": "pedram"},
    {"id": 4, "name": "aziz"},
    {"id": 5, "name": "zahra"},
    {"id": 6, "name": "ali"},
    {"id": 7, "name": "ali"},
]


# /names (GET(RETRIEVE),POST(CREATE))
"""
@app.get("/names")
def retieve_name_list(q: str | None = None):
    if q:
        for item in names_list:
            return [item for item in names_list if item["name"] == q]
            # [operation, iteration , condition]
            # [    O    ,     I     ,     T    ] OIT
    return names_list
"""

# or use Optional in  query parameter
"""
from typing import Optional
@app.get("/names")
def retieve_name_list(q: Optional[str] = None):
    if q:
        for item in names_list:
            return [item for item in names_list if item["name"] == q]
    return names_list
"""

# or with Annotation
"""
from typing import Annotated
from fastapi import Query
@app.get("/names")
def retieve_name_list(q: Annotated[str | None, Query(max_length=30)] = None):
    if q:        
        return [item for item in names_list if item["name"] == q]
    return names_list
"""

# or with out annotaions
from fastapi import Query
@app.get("/names")
def retieve_name_list(q: str | None = Query(alias="search", description="it will be searched with the title you inputed",example="ali" , default=None, max_length=30)):
    if q:        
        return [item for item in names_list if item["name"] == q]
    return names_list


from fastapi import status, HTTPException, Form, Body
@app.post("/names", status_code=status.HTTP_201_CREATED)
def create_name(name: str = Body(embed=True)):
    id_for_new_name = len(names_list) + 1
    names_list.append({"id": id_for_new_name, "name": name})
    return {"detail": "new name created", "new name": names_list[-1]}


# /names/:id (GET(RETRIEVE),PUT/PATCH(UPDATE),DELETE)
from fastapi import Path
@app.get("/names/{name_id}")
def retrieve_name_detail(name_id: int = Path(alias="name id", title="Name ID", description="this is an integer as name id")):
    for name in names_list:
        if name["id"] == name_id:
            return name
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")


@app.put("/names/{name_id}", status_code=status.HTTP_200_OK)
def update_name_detail(name_id: int = Path() , name: str = Form()):
    for item in names_list:
        if item["id"] == name_id:
            item["name"] = name
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")


from fastapi.responses import JSONResponse

@app.delete("/names/{name_id}")
def delete_name(name_id: int):
    for item in names_list:
        if item["id"] == name_id:
            names_list.remove(item)
            names_list[:] = [{"id": i+1, "name": n["name"]}
                             for i, n in enumerate(names_list)]
            return JSONResponse(content={"detail": f"{item} deleted!"}, status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")


@app.get("/")
def root():
    msg = {"message": "Hello World!"}
    return JSONResponse(content=msg, status_code=status.HTTP_202_ACCEPTED)


from fastapi import File, UploadFile
@app.post("/file")
def file(file: bytes = File(...)):
    print(file)
    return {"file_size" : len(file)}


@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    msg = await file.read()
    print(file.__dict__)
    return {"filename" : file.filename, "content_type": file.content_type, "file_size": len(msg)}


from typing import List
@app.post("/uploadmultifile")
async def upload_multi_file(files: List[UploadFile]):
    return [{"filename" : file.filename, "content_type": file.content_type} for file in files]

