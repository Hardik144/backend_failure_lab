from dataclasses import dataclass


@dataclass(frozen=True)
class OperationResult:
    status: str
    delay_seconds: float
