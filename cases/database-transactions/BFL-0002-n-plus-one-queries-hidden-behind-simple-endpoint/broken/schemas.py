from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    item_name: str
    total_cents: int


class UserWithOrdersResponse(BaseModel):
    id: int
    email: str
    orders: list[OrderResponse]
