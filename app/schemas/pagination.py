"""分页工具模块。"""


def build_paginated_data(items: list, total: int, page: int, page_size: int) -> dict:
    """构建分页响应数据，入口处对参数做防御性校验。"""
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
