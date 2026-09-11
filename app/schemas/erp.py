from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.crm import CrmOrderCreated


class ErpCustomer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    full_name: str
    email: str
    phone_number: str


class ErpLineItem(BaseModel):
    product_code: str
    description: str
    quantity: int
    unit_price: Decimal


class ErpOrder(BaseModel):
    external_order_id: str
    customer: ErpCustomer
    lines: list[ErpLineItem]
    state: str
    amount: Decimal
    currency: str

    @classmethod
    def from_crm(cls, order: CrmOrderCreated, target_currency: str = "EUR") -> "ErpOrder":
        rate = {"EUR": Decimal("1"), "USD": Decimal("0.92"), "GBP": Decimal("1.17")}.get(order.currency)
        if rate is None:
            raise ValueError(f"unsupported currency: {order.currency}")
        source_total = sum(item.unit_price * item.quantity for item in order.items)
        if abs(source_total - order.total_price) > Decimal("0.01"):
            raise ValueError("total_price does not match item totals")
        return cls(
            external_order_id=order.order_id,
            customer=ErpCustomer(full_name=order.lead.name, email=order.lead.email, phone_number=order.lead.phone),
            lines=[ErpLineItem(product_code=i.sku, description=i.name, quantity=i.quantity, unit_price=(i.unit_price * rate).quantize(Decimal("0.01"))) for i in order.items],
            state=order.status.upper(),
            amount=(order.total_price * rate).quantize(Decimal("0.01")),
            currency=target_currency,
        )
