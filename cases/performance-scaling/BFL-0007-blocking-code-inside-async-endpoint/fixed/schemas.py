from pydantic import BaseModel


class OperationResponse(BaseModel):
    status: str
    delay_seconds: float
