"""统一序列化模块。

将各路由中分散的序列化函数集中管理，确保同一模型在不同接口中
返回一致的 JSON 结构。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Category, Post, Tag
    from app.models.site_settings import SiteSettings


def serialize_post(post: Post) -> dict:
    """将 Post ORM 对象序列化为前端所需的字典。"""
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "content": post.content,
        "category_id": post.category_id,
        "category_name": post.category.name if post.category else None,
        "category_slug": post.category.slug if post.category else None,
        "tag_ids": [tag.id for tag in post.tags],
        "tags": [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in post.tags],
        "published_at": post.published_at.isoformat() if post.published_at else None,
    }


def serialize_category(category: Category) -> dict:
    """将 Category ORM 对象序列化为前端所需的字典。"""
    return {"id": category.id, "name": category.name, "slug": category.slug}


def serialize_tag(tag: Tag) -> dict:
    """将 Tag ORM 对象序列化为前端所需的字典。"""
    return {"id": tag.id, "name": tag.name, "slug": tag.slug}


def serialize_author(settings: SiteSettings) -> dict:
    """将 SiteSettings 中的作者信息序列化为前端所需的字典。"""
    return {
        "blog_title": settings.blog_title,
        "name": settings.author_name,
        "bio": settings.author_bio,
        "email": settings.author_email,
        "avatar": settings.author_avatar,
        "link": settings.author_link,
    }
