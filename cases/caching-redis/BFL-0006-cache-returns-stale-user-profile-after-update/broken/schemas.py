from pydantic import BaseModel


class ProfileResponse(BaseModel):
    user_id: int
    name: str


class ProfileUpdate(BaseModel):
    name: str
