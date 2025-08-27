# core/expenses/routs.py
from fastapi import status, HTTPException, Path, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.db import get_db
from expenses.models import ExpenseModel
from users.models import UserModel
from fastapi import APIRouter
from math import ceil
from expenses.schemas import ExpenseCreateSchema, ExpenseUpdateSchema, ExpenseResponseSchema
from auth.jwt_cookie_auth import get_current_user_from_cookies


router = APIRouter(tags=["expenses"],)


# ++++ CRUD with DB ++++

@router.get("/expenses",)
def retrieve_expense_list(
    q: str | None = Query(default=None, alias="search", description="case-insensitive match on description", max_length=50),
    page: int = Query(1, ge=1, description="page number"),
    limit: int = Query(10, le=50, description="number of items per page"),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user_from_cookies),
):
    query = db.query(ExpenseModel).filter_by(user_id=user.id)
    if q:
        query = query.filter(ExpenseModel.description.ilike(q.strip()))

    total_items = query.count()
    total_pages = ceil(total_items / limit) if total_items else 1

    offset = (page - 1) * limit

    results = query.offset(offset).limit(limit).all()

    return {"page": page, "total_pages": total_pages, "total_items": total_items, "next_page": page + 1 if page < total_pages else None, "prev_page": page - 1 if page > 1 else None, "result": results}


@router.get("/expenses/{expense_id}")
def retrieve_expense_detail(expense_id: int = Path(..., description="Expense ID"), db: Session = Depends(get_db), user: UserModel = Depends(get_current_user_from_cookies)):
    expense_obj = db.query(ExpenseModel).filter_by(id=expense_id, user_id=user.id).first()
    if not expense_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")
    return expense_obj


@router.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreateSchema, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user_from_cookies)):
    data = payload.model_dump()
    data.update({"user_id": user.id})
    expense_obj = ExpenseModel(**data)
    db.add(expense_obj)
    db.commit()
    db.refresh(expense_obj)
    return expense_obj


@router.put("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def update_expense_detail(
    payload: ExpenseUpdateSchema, expense_id: int = Path(..., description="ID of the expense to update"), db: Session = Depends(get_db), user: UserModel = Depends(get_current_user_from_cookies)
):
    expense_obj = db.query(ExpenseModel).filter_by(id=expense_id, user_id=user.id).first()
    if not expense_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")

    before = ExpenseResponseSchema.model_validate(expense_obj, from_attributes=True).model_dump()
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense_obj, field, value)
    db.commit()
    db.refresh(expense_obj)
    after = ExpenseResponseSchema.model_validate(expense_obj, from_attributes=True).model_dump()

    return {"detail": f"expense {expense_id} updated", "before": before, "after": after}


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), user: UserModel = Depends(get_current_user_from_cookies)):
    expense_obj = db.query(ExpenseModel).filter_by(id=expense_id, user_id=user.id).first()
    if not expense_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="object not found")

    db.delete(expense_obj)
    db.commit()
    return JSONResponse(content={"detail": f"expense {expense_id} deleted!"}, status_code=status.HTTP_200_OK)
