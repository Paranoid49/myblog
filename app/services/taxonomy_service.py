from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Category, Tag
from app.utils.text import slugify

if TYPE_CHECKING:
    from app.models import Post


def list_taxonomy(db: Session) -> tuple[list[Category], list[Tag]]:
    """查询所有分类和标签，按名称排序返回。"""
    categories = list(db.execute(select(Category).order_by(Category.name.asc())).scalars().all())
    tags = list(db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all())
    return categories, tags


def create_category(db: Session, name: str) -> Category:
    """创建分类并持久化。"""
    category = Category(name=name, slug=slugify(name))
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def create_tag(db: Session, name: str) -> Tag:
    """创建标签并持久化。"""
    tag = Tag(name=name, slug=slugify(name))
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def get_published_posts_by_category(
    db: Session, slug: str, page: int = 1, page_size: int = 20
) -> tuple[Category | None, list[Post], int]:
    """按分类查询已发布文章（数据库层过滤+分页）"""
    from app.models import Post

    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    category = db.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()
    if not category:
        return None, [], 0

    base = select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(
        Post.category_id == category.id,
        Post.published_at.is_not(None),
    )
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar() or 0
    posts = list(
        db.execute(base.order_by(Post.published_at.desc()).offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return category, posts, total


def get_published_posts_by_tag(
    db: Session, slug: str, page: int = 1, page_size: int = 20
) -> tuple[Tag | None, list[Post], int]:
    """按标签查询已发布文章（数据库层过滤+分页）"""
    from app.models import Post, post_tags

    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    tag = db.execute(select(Tag).where(Tag.slug == slug)).scalar_one_or_none()
    if not tag:
        return None, [], 0

    base = select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(
        Post.published_at.is_not(None),
        Post.id.in_(select(post_tags.c.post_id).where(post_tags.c.tag_id == tag.id)),
    )
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar() or 0
    posts = list(
        db.execute(base.order_by(Post.published_at.desc()).offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return tag, posts, total


def update_category(db: Session, category: Category, new_name: str) -> Category:
    """重命名分类"""
    category.name = new_name
    category.slug = slugify(new_name)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    """删除分类，关联文章迁移至默认分类"""
    from app.services.post_service import resolve_category_id

    default_id = resolve_category_id(db, None)
    # 将该分类下的文章迁移到默认分类
    for post in category.posts:
        post.category_id = default_id
    db.delete(category)
    db.commit()


def update_tag(db: Session, tag: Tag, new_name: str) -> Tag:
    """重命名标签"""
    tag.name = new_name
    tag.slug = slugify(new_name)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: Tag) -> None:
    """删除标签，自动解除与文章的关联"""
    tag.posts = []  # 清空关联
    db.delete(tag)
    db.commit()


def category_exists_by_name(db: Session, name: str) -> bool:
    """按名称检查分类是否已存在"""
    return db.execute(select(Category.id).where(Category.slug == slugify(name))).first() is not None


def tag_exists_by_name(db: Session, name: str) -> bool:
    """按名称检查标签是否已存在"""
    return db.execute(select(Tag.id).where(Tag.slug == slugify(name))).first() is not None


def get_tags_by_ids(db: Session, tag_ids: list[int]) -> list[Tag]:
    """按 ID 列表批量获取标签"""
    if not tag_ids:
        return []
    return list(db.execute(select(Tag).where(Tag.id.in_(tag_ids))).scalars().all())
