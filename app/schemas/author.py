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
