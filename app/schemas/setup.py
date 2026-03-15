from pydantic import BaseModel, field_validator


class SetupStatusResponse(BaseModel):
    """初始化状态响应体"""

    initialized: bool
    database_exists: bool


class SetupRequest(BaseModel):
    """站点初始化请求体"""

    blog_title: str
    username: str
    password: str
    confirm_password: str

    @field_validator("blog_title", "username", "password")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must_not_be_blank")
        return value
