"""统一序列化模块。

将 ORM 模型转换为结构化的 Pydantic 响应对象，确保同一模型
在不同接口中返回一致的 JSON 结构。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from app.models import Category, Post, Tag
    from app.models.site_settings import SiteSettings


class TagResponse(BaseModel):
    """标签响应体"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class CategoryResponse(BaseModel):
    """分类响应体"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class PostResponse(BaseModel):
    """文章响应体"""

    id: int
    title: str
    slug: str
    summary: str | None
    content: str
    category_id: int | None
    category_name: str | None = None
    category_slug: str | None = None
    tag_ids: list[int] = []
    tags: list[TagResponse] = []
    published_at: str | None = None


class AuthorResponse(BaseModel):
    """作者信息响应体"""

    blog_title: str
    name: str
    bio: str
    email: str
    avatar: str
    link: str


def serialize_post(post: Post) -> dict:
    """将 Post ORM 对象序列化为前端所需的字典。"""
    return PostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        content=post.content,
        category_id=post.category_id,
        category_name=post.category.name if post.category else None,
        category_slug=post.category.slug if post.category else None,
        tag_ids=[tag.id for tag in post.tags],
        tags=[TagResponse.model_validate(tag) for tag in post.tags],
        published_at=post.published_at.isoformat() if post.published_at else None,
    ).model_dump()


def serialize_category(category: Category) -> dict:
    """将 Category ORM 对象序列化为前端所需的字典。"""
    return CategoryResponse.model_validate(category).model_dump()


def serialize_tag(tag: Tag) -> dict:
    """将 Tag ORM 对象序列化为前端所需的字典。"""
    return TagResponse.model_validate(tag).model_dump()


def serialize_author(settings: SiteSettings) -> dict:
    """将 SiteSettings 中的作者信息序列化为前端所需的字典。"""
    return AuthorResponse(
        blog_title=settings.blog_title,
        name=settings.author_name,
        bio=settings.author_bio,
        email=settings.author_email,
        avatar=settings.author_avatar,
        link=settings.author_link,
    ).model_dump()
