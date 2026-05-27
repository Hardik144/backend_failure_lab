from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    user_id: int
    item_name: str
    total_cents: int
