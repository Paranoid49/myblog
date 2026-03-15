from pydantic import BaseModel, field_validator


class NameCreateRequest(BaseModel):
    """分类/标签创建请求体"""

    name: str

    @field_validator("name")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value
