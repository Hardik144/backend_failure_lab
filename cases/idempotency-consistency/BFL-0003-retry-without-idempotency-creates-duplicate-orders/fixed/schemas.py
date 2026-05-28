from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    item_name: str
    total_cents: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    item_name: str
    total_cents: int
