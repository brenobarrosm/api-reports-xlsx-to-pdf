from datetime import datetime

from typing import Literal

from fastapi import UploadFile
from pydantic import BaseModel, Field


class ReportFilters(BaseModel):
    type: str
    value: str | None = Field(default=None)


class ReportInDTO(BaseModel):
    file: UploadFile
    filters: ReportFilters


class Metric(BaseModel):
    metric: str
    value: str | int | float


class Section(BaseModel):
    name: str
    metrics: list[Metric]


class ReportInfoOutDTO(BaseModel):
    title: str
    sections: list[Section]
    created_at: datetime = Field(default=datetime.now())
