from pydantic import BaseModel, Field


class ColumnRenameRequest(BaseModel):
    title: str = Field(min_length=1)


class CardCreateRequest(BaseModel):
    column_id: str
    title: str = Field(min_length=1)
    details: str = ""


class CardUpdateRequest(BaseModel):
    title: str = Field(min_length=1)
    details: str = ""


class CardMoveRequest(BaseModel):
    column_id: str
    position: int = Field(ge=0)
