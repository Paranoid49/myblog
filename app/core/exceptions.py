"""应用异常体系。

统一使用 raise 异常替代 return error_response，
由全局异常处理器转换为统一 API 响应格式。
"""


class AppError(Exception):
    """应用业务异常基类"""

    def __init__(self, message: str, code: int, status_code: int = 400) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """资源不存在"""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message, code, 404)


class ConflictError(AppError):
    """冲突（如重复创建）"""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message, code, 409)


class UnauthorizedError(AppError):
    """未认证"""

    def __init__(self, message: str = "unauthorized", code: int = 1002) -> None:
        super().__init__(message, code, 401)


class TooManyRequestsError(AppError):
    """请求过多"""

    def __init__(self, message: str = "too_many_attempts", code: int = 1006) -> None:
        super().__init__(message, code, 429)
