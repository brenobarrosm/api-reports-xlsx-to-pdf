from fastapi import HTTPException
from pydantic import BaseModel

ERROR_MSG = 'INVALID_FILE_TYPE_EXCEPTION'


class InvalidFileTypeException(HTTPException):
    def __init__(self) -> None:
        self.status_code = 409
        self.detail = ERROR_MSG


class InvalidFileTypeModel(BaseModel):
    error_msg: str | None = ERROR_MSG
