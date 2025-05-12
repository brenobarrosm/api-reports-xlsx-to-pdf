from pydantic import BaseModel


class OneDriveRequest(BaseModel):
    url: str