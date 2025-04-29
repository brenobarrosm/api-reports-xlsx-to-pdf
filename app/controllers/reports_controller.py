from fastapi import APIRouter, Query, UploadFile, File, Form, Depends
from starlette import status

from app.entities.report import ReportFilters, ReportInDTO
from app.services.get_report_info_service import GetReportInfoService

router = APIRouter(prefix='/reports')


get_report_info_service = GetReportInfoService()

def get_report_filter(
        filter_type: str = Form(...),
        scope: str = Form(...),
        value: str = Form(...)
) -> ReportFilters:
    return ReportFilters(type=filter_type, scope=scope, value=value)


@router.post('/info')
async def get_report_info(
        file: UploadFile = File(...),
        filters: ReportFilters = Depends(get_report_filter)
):
    return get_report_info_service.execute(ReportInDTO(
        file=file,
        filters=filters
    ))
