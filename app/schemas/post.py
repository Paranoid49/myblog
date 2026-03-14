from pydantic import BaseModel, Field, field_validator


class PostCreate(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int
    tag_ids: list[int] = Field(default_factory=list)


class AdminPostCreateRequest(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("title", "content")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


class AdminPostUpdateRequest(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("title", "content")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value


class ImportMarkdownRequest(BaseModel):
    markdown: str
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("markdown")
    @classmethod
    def _markdown_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value
