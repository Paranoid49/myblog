from pydantic import BaseModel, field_validator

from app.schemas.validators import not_blank


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
        return not_blank(value)

    @field_validator("password")
    @classmethod
    def _password_complexity(cls, value: str) -> str:
        """密码复杂度校验：至少 8 个字符，且同时包含字母和数字"""
        v = value.strip()
        if len(v) < 8:
            raise ValueError("password_too_short")
        if not any(c.isdigit() for c in v):
            raise ValueError("password_needs_digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("password_needs_letter")
        return value
