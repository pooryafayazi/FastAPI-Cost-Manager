# core/expenses/schemas.py
from datetime import datetime
from pydantic import BaseModel, field_validator, Field


class BaseExpenseSchema(BaseModel):
    description: str = Field(
        ..., description="this is a short description of your expense.", min_length=3
    )
    amount: int = Field(
        default=1,
        lt=10000000000,
        json_schema_extra={"unit": "dollars"},
        description="this is amount of your expense",
    )

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


class ExpenseUpdateSchema(BaseExpenseSchema):
    pass


class ExpenseCreateSchema(BaseExpenseSchema):
    pass


class ExpenseResponseSchema(BaseExpenseSchema):
    id: int = Field(..., description="Unique expense identifier")
    create_date: datetime | None = None
    updated_date: datetime | None = None

    model_config = {"from_attributes": True}
