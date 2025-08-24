# core/main.py
from fastapi import FastAPI, status, HTTPException, Body, Path, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db import get_db
from models import Expense


app = FastAPI()

expenses_list = []


app = FastAPI(title="Expense Manager (DB-backed)")

# Creating tables at startup
"""
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
"""

# CRUD with DB

@app.get("/expenses")
def retrieve_expense_list(q: str | None = Query(default=None, alias="search", description="case-insensitive match on description", max_length=50), db: Session = Depends(get_db)):
    query = db.query(Expense)
    if q:
        query = query.filter(Expense.description.ilike(q.strip()))
        # query = query.filter(Expense.description.ilike(f"%{q.strip()}%"))
    items = query.order_by(Expense.id.desc()).all()
    return [{"id": e.id, "description": e.description, "amount": e.amount} for e in items]


"""
@app.get("/expenses")
def retieve_expense_list(q: str | None = Query(alias="search", description="it will be searched with the title you inputed",example="loan" , default=None, max_length=50), db:Session = Depends(get_db)):
    if q:        
        return [item for item in expenses_list if item["description"].lower() == q.lower()]
    return expenses_list
"""


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(description: str = Body(..., embed=True, min_length=3, max_length=50), amount: int = Body(..., embed=True, gt=0, lt=10_000_000_000), db: Session = Depends(get_db)):
    exp = Expense(description=description.strip(), amount=amount)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return {"detail": "new expense created", "expense": {"id": exp.id, "description": exp.description, "amount": exp.amount}}


"""
def _generate_unique_id(existing_ids: set[int], max_tries: int = 1000) -> int:
    for _ in range(max_tries):
        cand = random.randint(1, 100)
        if cand not in existing_ids:
            return cand
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not generate unique id")


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(description: str = Body(...), amount:int = Body(...)):
    # new_id = len(expenses_list) + 1
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expenses_list.append({"id": new_id, "description": description, "amount": amount})
    return {"detail": "new expense created", "new expense is": expenses_list[-1]}
"""


@app.get("/expenses/{expense_id}")
def retrieve_expense_detail(expense_id: int = Path(..., title="Expense ID"), db: Session = Depends(get_db)):
    exp = db.get(Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
    return {"id": exp.id, "description": exp.description, "amount": exp.amount}


"""
@app.get("/expenses/{expense_id}")
def retrieve_expense_detail(expense_id: int = Path(..., title="Expense ID", description="this is an integer as expense id")):
    for item in expenses_list:
        if item["id"] == expense_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
"""


@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(expense_id: int = Path(...), description: str = Body(..., embed=True, min_length=3, max_length=50), amount: int = Body(..., embed=True, gt=0, lt=10_000_000_000), db: Session = Depends(get_db)):
    exp = db.get(Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")

    exp.description = description.strip()
    exp.amount = amount
    db.commit()
    db.refresh(exp)
    return {"detail": "expense updated", "expense": {"id": exp.id, "description": exp.description, "amount": exp.amount}}


"""
@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(expense_id: int = Path() , description: str = Body(), amount: int = Body()):
    for item in expenses_list:
        if item["id"] == expense_id:
            item["description"] = description
            item["amount"] = amount
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
"""

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    exp = db.get(Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")

    db.delete(exp)
    db.commit()
    return JSONResponse(content={"detail": f"expense {expense_id} deleted!"}, status_code=status.HTTP_200_OK)


"""
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    for item in expenses_list:
        if item["id"] == expense_id:
            expenses_list.remove(item)
            # expenses_list[:] = [{"id": i+1, "description": n["description"], "amount": n["amount"]} for i, n in enumerate(expenses_list)]
            return JSONResponse(content={"detail": f"{item} deleted!"}, status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
"""

