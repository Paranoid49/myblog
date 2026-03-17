"""Schema 公共验证器。"""


def not_blank(value: str) -> str:
    """通用非空校验器，可在 field_validator 中直接调用"""
    if not value.strip():
        raise ValueError("must_not_be_blank")
    return value
