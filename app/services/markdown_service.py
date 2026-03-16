"""Markdown 处理服务。

提供 Markdown 标题提取和文章导出等功能。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Post


def extract_markdown_title(markdown: str) -> str:
    """从 Markdown 内容中提取标题。

    优先使用第一个 H1 标题（``# 标题``），
    若无 H1 则回退到首个非空行（截取前 80 字符），
    均无内容时返回 ``"Untitled"``。
    """
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or "Untitled"

    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:80]

    return "Untitled"


def build_markdown_export(post: Post) -> dict[str, str]:
    """将文章导出为 Markdown 格式。

    返回包含 ``filename`` 和 ``markdown`` 两个键的字典，
    其中 ``filename`` 使用文章 slug，``markdown`` 以 H1 标题开头。
    """
    return {
        "filename": f"{post.slug}.md",
        "markdown": f"# {post.title}\n\n{post.content}",
    }
