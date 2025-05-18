from fastapi import APIRouter, UploadFile, File, Form, Depends, Response

from app.entities.report import ReportFilters, ReportInDTO, ReportInfoOutDTO
from app.services.get_report_info_service import GetReportInfoService
from app.services.get_report_file_pdf_service import GetReportFilePdfService
from app.utils.auth import get_current_user

router = APIRouter(prefix='/reports')

get_report_info_service = GetReportInfoService()
get_report_file_pdf_service = GetReportFilePdfService()


def get_report_filter(
        filter_type: str = Form(...),
        value: str = Form(...)
) -> ReportFilters:
    return ReportFilters(type=filter_type, value=value)


@router.post('/info')
async def get_report_info(
        file: UploadFile = File(...),
        filters: ReportFilters = Depends(get_report_filter),
) -> ReportInfoOutDTO:
    return get_report_info_service.execute(ReportInDTO(file=file, filters=filters))


@router.post('/pdf')
async def get_report_pdf(
        report_info: ReportInfoOutDTO,
):
    pdf_bytes = get_report_file_pdf_service.execute(report_info)
    return Response(content=pdf_bytes, media_type="application/pdf")
