import re

from pydantic import BaseModel, Field, field_validator

from app.schemas.validators import not_blank

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class AuthorProfileUpdateRequest(BaseModel):
    """作者信息更新请求体"""

    name: str = Field(..., max_length=100)
    bio: str
    email: str = Field(default="", max_length=200)
    avatar: str = Field(default="", max_length=500)
    link: str = Field(default="", max_length=500)

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        return not_blank(value)

    @field_validator("bio", "email", "avatar", "link")
    @classmethod
    def _trim_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        v = value.strip()
        if v and not _EMAIL_RE.match(v):
            raise ValueError("invalid_email_format")
        return v

    @field_validator("link", "avatar")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        v = value.strip()
        if v and not v.startswith(("http://", "https://", "/")):
            raise ValueError("invalid_url_format")
        return v
