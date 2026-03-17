from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import not_blank


class AdminPostWriteRequest(BaseModel):
    """后台文章创建/更新统一请求体"""

    title: str = Field(..., max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("title", "content")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        return not_blank(value)


class ImportMarkdownRequest(BaseModel):
    markdown: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("markdown")
    @classmethod
    def _markdown_not_blank(cls, value: str) -> str:
        return not_blank(value)
