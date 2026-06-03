from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}
