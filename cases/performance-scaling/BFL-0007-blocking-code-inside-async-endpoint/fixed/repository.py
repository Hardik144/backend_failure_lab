from .models import OperationResult


WORK_SECONDS = 0.08


def build_operation_result() -> OperationResult:
    return OperationResult(status="done", delay_seconds=WORK_SECONDS)
