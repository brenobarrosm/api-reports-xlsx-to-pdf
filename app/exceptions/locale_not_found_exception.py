from fastapi import HTTPException
from pydantic import BaseModel

ERROR_MSG = 'LOCALE_NOT_FOUND_EXCEPTION'


class LocaleNotFoundException(HTTPException):
    def __init__(self) -> None:
        self.status_code = 404
        self.detail = ERROR_MSG


class LocaleNotFoundModel(BaseModel):
    error_msg: str | None = ERROR_MSG
