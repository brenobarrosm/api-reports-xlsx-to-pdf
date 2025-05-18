from fastapi import HTTPException
from pydantic import BaseModel

ERROR_MSG = 'INVALID_USER_CREDENTIALS_EXCEPTION'


class InvalidUserCredentialsException(HTTPException):
    def __init__(self) -> None:
        self.status_code = 401
        self.detail = ERROR_MSG


class InvalidUserCredentialsModel(BaseModel):
    error_msg: str | None = ERROR_MSG
