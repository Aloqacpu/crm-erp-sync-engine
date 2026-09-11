from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class Lead(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str
    phone: str = Field(min_length=7, max_length=32)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        normalized = "".join(character for character in value if character.isdigit() or character == "+")
        if normalized.startswith("00"):
            normalized = "+" + normalized[2:]
        if len(normalized.lstrip("+")) < 7:
            raise ValueError("phone number is too short")
        return normalized


class OrderItem(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    quantity: int = Field(ge=1, le=100000)
    unit_price: Decimal = Field(ge=0, decimal_places=2)


class CrmOrderCreated(BaseModel):
    order_id: str = Field(min_length=1, max_length=128)
    lead: Lead
    items: list[OrderItem] = Field(min_length=1)
    status: str = Field(min_length=1, max_length=32)
    total_price: Decimal = Field(ge=0, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()
