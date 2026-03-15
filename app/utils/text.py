"""文本处理工具模块。

提供 slug 生成等与文本转换相关的通用工具函数，
供 service 层和路由层共享使用，避免循环依赖。
"""

import re

from pypinyin import Style, lazy_pinyin


def _normalize_chunks(value: str) -> list[str]:
    """将混合中英文字符串拆分为拼音/英文片段列表。

    处理规则：
    - ASCII 字母和数字保留并转小写
    - 中文字符转为拼音
    - 其他字符（符号、空格等）作为分隔符丢弃
    """
    chunks: list[str] = []
    current: list[str] = []

    for char in value.strip():
        if char.isascii() and char.isalnum():
            current.append(char.lower())
            continue

        if current:
            chunks.append("".join(current))
            current = []

        if "\u4e00" <= char <= "\u9fff":
            chunks.extend(lazy_pinyin(char, style=Style.NORMAL))

    if current:
        chunks.append("".join(current))

    return chunks


def slugify(value: str) -> str:
    """将标题文本转换为 URL 友好的 slug。

    支持中英文混合标题，中文部分转为拼音。
    当结果为空时回退返回 ``"post"``。
    """
    chunks = _normalize_chunks(value)
    slug = "-".join(chunk for chunk in chunks if chunk)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "post"
