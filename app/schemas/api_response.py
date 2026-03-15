from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int
    message: str
    data: dict | list | None


def ok_response(data: dict | list | None = None, message: str = "ok", status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": 0, "message": message, "data": data})


def build_error_detail(message: str, code: int) -> dict:
    """构造统一的错误响应字典，供 HTTPException.detail 和 error_response 共享。"""
    return {"code": code, "message": message, "data": None}


def error_response(message: str, status_code: int, code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=build_error_detail(message, code))
