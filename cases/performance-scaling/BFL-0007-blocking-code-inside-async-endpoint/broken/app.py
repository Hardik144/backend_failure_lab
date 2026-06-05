import time

from fastapi import FastAPI

from repository import WORK_SECONDS, build_operation_result
from schemas import OperationResponse


def create_app() -> FastAPI:
    app = FastAPI(title="BFL-0007 Broken")

    @app.get("/slow-operation", response_model=OperationResponse)
    async def slow_operation() -> OperationResponse:
        time.sleep(WORK_SECONDS)
        result = build_operation_result()
        return OperationResponse(status=result.status, delay_seconds=result.delay_seconds)

    return app
