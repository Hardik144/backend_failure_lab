from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    item_name: str


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    next_cursor: int | None
