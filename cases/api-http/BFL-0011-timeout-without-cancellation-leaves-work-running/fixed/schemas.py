from pydantic import BaseModel


class ExportResponse(BaseModel):
    id: int
    status: str
    result: str | None
