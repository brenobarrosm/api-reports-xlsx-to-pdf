from io import BytesIO

from fastapi import APIRouter, Query, Response
from starlette import status

from app.entities.file import OneDriveRequest
from app.services.get_file_from_onedrive_service import GetFileFromOneDriveService

router = APIRouter(prefix='/files')


get_file_from_onedrive_service = GetFileFromOneDriveService()


@router.post('/onedrive')
def get_file_from_onedrive(data: OneDriveRequest):
    xlsx_bytes = get_file_from_onedrive_service.execute(data.url)
    return Response(content=xlsx_bytes.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


