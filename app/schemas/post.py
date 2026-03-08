from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str
    summary: str | None = None
    content: str
    category_id: int
    tag_ids: list[int] = Field(default_factory=list)
