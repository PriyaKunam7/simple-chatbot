# app/schemas.py

from pydantic import BaseModel, Field, field_validator


class OrderCreate(BaseModel):
    product_id: str = Field(..., example="PROD001")
    customer_id: str = Field(..., example="CUST001")
    seller_id: str = Field(..., example="SELLER001")
    amount: float = Field(..., example=120.50)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        if value < 10:
            raise ValueError("Amount must be at least $10")

        if value > 100000:
            raise ValueError("Amount cannot exceed $100,000")

        return round(value, 2)


class OrderUpdate(BaseModel):
    status: str = Field(..., example="shipped")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = [
            "pending",
            "paid",
            "shipped",
            "delivered",
            "cancelled",
            "settled"
        ]

        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")

        return value