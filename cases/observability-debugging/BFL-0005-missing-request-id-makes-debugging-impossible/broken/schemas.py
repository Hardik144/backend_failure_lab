from pydantic import BaseModel


class PaymentResponse(BaseModel):
    status: str
    user_id: int
