# main.py
from fastapi import FastAPI
import random


app = FastAPI()

expenses_list = []

def _generate_unique_id(existing_ids: set[int], max_tries: int = 1000) -> int:
    for _ in range(max_tries):
        cand = random.randint(1, 100)
        if cand not in existing_ids:
            return cand
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not generate unique id")


from fastapi import status, HTTPException, Body
@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(description: str = Body(...), amount:int = Body(...)):
    # new_id = len(expenses_list) + 1
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expenses_list.append({"id": new_id, "description": description, "amount": amount})
    return {"detail": "new expense created", "new expense is": expenses_list[-1]}


from fastapi import Query

@app.get("/expenses")
def retieve_expense_list(q: str | None = Query(alias="search", description="it will be searched with the title you inputed",example="loan" , default=None, max_length=50)):
    if q:        
        return [item for item in expenses_list if item["description"].lower() == q.lower()]
    return expenses_list


from fastapi import Path

@app.get("/expenses/{expense_id}")
def retrieve_expense_detail(expense_id: int = Path(..., title="Expense ID", description="this is an integer as expense id")):
    for item in expenses_list:
        if item["id"] == expense_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")


@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(expense_id: int = Path() , description: str = Body(), amount: int = Body()):
    for item in expenses_list:
        if item["id"] == expense_id:
            item["description"] = description
            item["amount"] = amount
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")


from fastapi.responses import JSONResponse

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for item in expenses_list:
        if item["id"] == expense_id:
            expenses_list.remove(item)
            # expenses_list[:] = [{"id": i+1, "description": n["description"], "amount": n["amount"]} for i, n in enumerate(expenses_list)]
            return JSONResponse(content={"detail": f"{item} deleted!"}, status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
