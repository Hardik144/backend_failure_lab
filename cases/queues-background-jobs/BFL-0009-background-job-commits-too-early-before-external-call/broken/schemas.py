from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: int
    status: str
    confirmation_sent: bool

    model_config = {"from_attributes": True}
