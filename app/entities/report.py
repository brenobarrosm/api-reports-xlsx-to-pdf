from datetime import datetime

from typing import Literal

from fastapi import UploadFile
from pydantic import BaseModel, Field


class ReportFilters(BaseModel):
    type: Literal['REGIONAL', 'PROFISSIONAL']
    scope: Literal['REGIÃO', 'UF', 'MUNICÍPIO', 'PROFISSIONAL']
    value: str | None = Field(default=None)


class ReportInDTO(BaseModel):
    file: UploadFile
    filters: ReportFilters


class Metric(BaseModel):
    metric: str
    value: str | int | float


class ReportInfoOutDTO(BaseModel):
    title: str
    metrics: list[Metric]
    created_at: datetime = Field(default=datetime.now())
