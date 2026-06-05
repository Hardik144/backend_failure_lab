from fastapi import FastAPI, HTTPException

from models import ExportJob
from repository import ExportTimeoutError, get_export, run_export
from schemas import ExportResponse


def create_app() -> FastAPI:
    app = FastAPI(title="BFL-0011 Fixed")
    app.state.exports = {100: ExportJob(id=100)}

    @app.post("/exports/{export_id}/run", response_model=ExportResponse)
    def run_export_endpoint(
        export_id: int,
        simulate_timeout: bool = False,
    ) -> ExportResponse:
        try:
            export = run_export(
                exports=app.state.exports,
                export_id=export_id,
                simulate_timeout=simulate_timeout,
            )
        except ExportTimeoutError as exc:
            raise HTTPException(status_code=504, detail="export timed out") from exc

        if export is None:
            raise HTTPException(status_code=404, detail="export not found")
        return ExportResponse(
            id=export.id,
            status=export.status,
            result=export.result,
        )

    @app.get("/exports/{export_id}", response_model=ExportResponse)
    def get_export_endpoint(export_id: int) -> ExportResponse:
        export = get_export(exports=app.state.exports, export_id=export_id)
        if export is None:
            raise HTTPException(status_code=404, detail="export not found")
        return ExportResponse(
            id=export.id,
            status=export.status,
            result=export.result,
        )

    return app
