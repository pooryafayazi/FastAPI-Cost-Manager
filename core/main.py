
# core/main.py
from fastapi import FastAPI, status, HTTPException, Body, Path, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db import get_db, Base, engine
from models import Expense
from contextlib import asynccontextmanager


app = FastAPI()

expenses_list = []



# Creating tables at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    print("application shutdown")


app = FastAPI(lifespan=lifespan, title="Expense Manager (DB-backed)")


# ++++ CRUD with DB ++++
"""
@app.get("/expenses")
def retrieve_expense_list(q: str | None = Query(default=None, alias="search",
                                                description="case-insensitive match on description",
                                                max_length=50), db: Session = Depends(get_db)):
    query = db.query(Expense)
    if q:
        query = query.filter(Expense.description.ilike(q.strip()))
        # query = query.filter(Expense.description.ilike(f"%{q.strip()}%"))
    items = query.order_by(Expense.id.desc()).all()
    return [{"id": e.id, "description": e.description, "amount": e.amount} for e in items]
"""


@app.get("/expenses")
def retieve_expense_list(q: str | None = Query(alias="search",
description="it will be searched with the title you inputed",example="loan" ,
default=None, max_length=50),
db:Session = Depends(get_db)):
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



def _generate_unique_id(existing_ids: set[int], max_tries: int = 100) -> int:
    for _ in range(max_tries):
        cand = random.randint(1, 100)
        if cand not in existing_ids:
            return cand
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not generate unique id")

    
"""
from dataclasses import dataclass

@dataclass
class Expense:
    description :str
    amount : int

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount must be a positive integer!")


@dataclass
class ExpenseResponse:
    id : int
    description :str
    amount : int
"""

"""
from fastapi import status, HTTPException, Body

@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(description: str = Body(...), amount:int = Body(...)):
    # new_id = len(expenses_list) + 1
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expenses_list.append({"id": new_id, "description": description, "amount": amount})
    return {"detail": "new expense created", "new expense is": expenses_list[-1]}
"""

"""
from fastapi import status, HTTPException, Body
@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(expense: Expense):
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expenses_list.append({"id": new_id, "description": expense.description, "amount": expense.amount})
    return {"detail": "new expense created", "new expense is": expenses_list[-1]}
"""

"""
from fastapi import status, HTTPException, Body
@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(expense: Expense):
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expenses_list.append({"id": new_id, "description": expense.description, "amount": expense.amount})
    response =  ExpenseResponse(new_id, expense.description, expense.amount)
    return {"detail": response}
"""

"""
from fastapi import Body
@app.post("/expenses", status_code=status.HTTP_201_CREATED,response_model=ExpenseResponse)
def create_expense(expense: Expense):
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expense_obj = {"id": new_id, "description": expense.description, "amount": expense.amount}
    expenses_list.append(expense_obj)
    return expense_obj
"""


@app.get("/expenses/{expense_id}")
def retrieve_expense_detail(expense_id: int = Path(..., title="Expense ID"), db: Session = Depends(get_db)):
    # exp = db.query(Expense).filter_by(id=expense_id).one_or_none()
    exp = db.get(Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
    # return {"id": exp.id, "description": exp.description, "amount": exp.amount}
    return exp


from schema import ExpenseCreateSchema, ExpenseResponseSchema,ExpenseUpdateSchema
from fastapi import Body
@app.post("/expenses", status_code=status.HTTP_201_CREATED, response_model=ExpenseResponseSchema)
def create_expense(expense: ExpenseCreateSchema):
    new_id = _generate_unique_id({item["id"] for item in expenses_list})
    expense_obj = {"id": new_id, "description": expense.description, "amount": expense.amount}
    expenses_list.append(expense_obj)
    return expense_obj


from fastapi import Query
from typing import List
@app.get("/expenses",response_model=List[ExpenseResponseSchema])
def retieve_expense_list(q: str | None = Query(alias="search", description="it will be searched with the title you inputed",example="loan" , default=None, max_length=50)):
    if q:        
        return [item for item in expenses_list if item["description"].lower() == q.lower()]
    return expenses_list





"""
@app.get("/expenses/{expense_id}",response_model=ExpenseResponseSchema)

def retrieve_expense_detail(expense_id: int = Path(..., title="Expense ID", description="this is an integer as expense id")):
    for item in expenses_list:
        if item["id"] == expense_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
"""



@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(expense_id: int = Path(...),
description: str = Body(..., embed=True, min_length=3, max_length=50),
amount: int = Body(..., embed=True, gt=0, lt=10_000_000_000), db: Session = Depends(get_db)):
    # exp = db.query(Expense).filter_by(id=expense_id).one_or_none()    
    exp = db.get(Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")

    exp.description = description.strip()
    exp.amount = amount
    db.commit()
    db.refresh(exp)
    # return {"detail": "expense updated", "expense": {"id": exp.id, "description": exp.description, "amount": exp.amount}}
    return {"detail": "expense updated", "expense": exp}


"""
@app.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK,response_model=ExpenseResponseSchema)
def update_expense_detail(expense : ExpenseUpdateSchema, expense_id: int = Path()):
    for item in expenses_list:
        if item["id"] == expense_id:
            item["description"] = expense.description
            item["amount"] = expense.amount
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

