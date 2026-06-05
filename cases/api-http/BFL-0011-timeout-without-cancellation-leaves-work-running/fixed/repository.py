from models import ExportJob


class ExportTimeoutError(Exception):
    pass


def get_export(exports: dict[int, ExportJob], export_id: int) -> ExportJob | None:
    return exports.get(export_id)


def run_export(
    exports: dict[int, ExportJob],
    export_id: int,
    *,
    simulate_timeout: bool = False,
) -> ExportJob | None:
    export = get_export(exports=exports, export_id=export_id)
    if export is None:
        return None

    export.status = "running"

    if simulate_timeout:
        export.status = "cancelled"
        export.result = None
        raise ExportTimeoutError("client timed out")

    export.status = "completed"
    export.result = "report.csv"
    return export
