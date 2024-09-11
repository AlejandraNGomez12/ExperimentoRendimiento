from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from enum import Enum
from sqlalchemy import Column, String
from sqlalchemy_utils import ChoiceType


class typeEnum(str, Enum):
    PDF = ".pdf"
    CSV = ".csv"
    DOC = ".doc"

class Report(SQLModel, table=True):
    id: Optional[UUID] = Field(default=uuid4(), primary_key=True)
    email:str
    filters:str
    type:typeEnum = Field(
        sa_column=Column(
            ChoiceType(typeEnum, impl=String()),
            nullable=False,
            default=typeEnum.PDF,
        )
    )
    menssageId:str
