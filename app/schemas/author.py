from pydantic import BaseModel, field_validator


class AuthorProfileUpdateRequest(BaseModel):
    """作者信息更新请求体"""

    name: str
    bio: str
    email: str
    avatar: str = ""
    link: str = ""

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value.strip()

    @field_validator("bio", "email", "avatar", "link")
    @classmethod
    def _trim_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        v = value.strip()
        if v and "@" not in v:
            raise ValueError("invalid_email_format")
        return v

    @field_validator("link", "avatar")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        v = value.strip()
        if v and not v.startswith(("http://", "https://", "/")):
            raise ValueError("invalid_url_format")
        return v
