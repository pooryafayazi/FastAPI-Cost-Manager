
# core/schema.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, Field
"""
class BaseExpenseSchema(BaseModel):
    description: str = Field(..., min_length=3, max_length=50)
    amount: int = Field(..., gt=0, lt=10_000_000_000)
    user_id: int
    wallet_id: int
    category_id: Optional[int] = None
    spent_date: datetime
"""


class BaseExpenseSchema(BaseModel):
    description : str = Field(..., description="this is a short description of your expense.", min_length=3)
    amount : int = Field(default=1, lt=10000000000, metadata={"unit": "dollars"}, description="this is amount of your expense")


    @field_validator("description")
    def validator_description(cls, value: str) -> str:
        value = value.strip()

        if len(value) > 50:
            raise ValueError("description must not exceed 50 characters")

        if not all(ch.isalpha() or ch.isspace() for ch in value):
            raise ValueError("description must contain only letters and spaces")
        if "  " in value:
            raise ValueError("use a single space between words")
        return value

"""
class ExpenseCreateSchema(BaseExpenseSchema):
    pass
"""

class ExpenseUpdateSchema(BaseExpenseSchema):

    
    @field_validator("amount")
    def validator_amount(cls, value):
        if value <= 0:
            raise ValueError("amount must be greater than 0")
        return value


class ExpenseCreateSchema(BaseExpenseSchema):
    pass


class ExpenseResponseSchema(BaseExpenseSchema):
"""
    id: int
    created_date: datetime
"""

    id : int = Field(..., description="Unique expense identifier")


class ExpenseUpdateSchema(BaseExpenseSchema):
    pass



#################### =================== ######################
# model_validate VS. model_validate_json for input
"""
class Expense(BaseModel):
    description :str
    amount : int

# if inpute data is a dictionary and if we want to use the dict for validate data and create Object :
data = {
     "description" : "loan",
     "amount" : 24
 }
ex = Expense.model_validate(data)

# if inpute data is a string with has json format and if we want to use the string for validate data and create Object :
data_json ='''
{
     "description" : "loan",
     "amount" : 24
}
'''
ex = Expense.model_validate_json(data_json)
"""


