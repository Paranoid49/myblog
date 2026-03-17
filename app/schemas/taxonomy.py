from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import not_blank


class NameCreateRequest(BaseModel):
    """分类/标签创建请求体"""

    name: str = Field(..., max_length=100)

    @field_validator("name")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        return not_blank(value)
