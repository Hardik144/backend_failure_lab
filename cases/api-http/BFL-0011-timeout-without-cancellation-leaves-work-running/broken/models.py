from dataclasses import dataclass


@dataclass
class ExportJob:
    id: int
    status: str = "pending"
    result: str | None = None
