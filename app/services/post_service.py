from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.hook_bus import hook_bus
from app.models import Category, Post, Tag
from app.schemas.post import ImportMarkdownRequest
from app.services.taxonomy_service import get_tags_by_ids
from app.utils.text import slugify


@dataclass
class PostCreatePayload:
    """文章创建/更新内部数据传递对象"""
    title: str
    summary: str | None
    content: str
    category_id: int
    tag_ids: list[int] = field(default_factory=list)


def resolve_category_id(db: Session, category_id: int | None) -> int:
    """解析分类 ID，未指定时自动获取或创建默认分类"""
    if category_id is not None:
        return category_id

    default_category = db.execute(select(Category).where(Category.slug == "default")).scalar_one_or_none()
    if default_category is None:
        default_category = db.execute(select(Category).where(Category.name == "默认分类")).scalar_one_or_none()

    if default_category is None:
        default_category = Category(name="默认分类", slug="default")
        db.add(default_category)
        db.flush()

    return default_category.id


def ensure_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug

    index = 2
    while f"{base_slug}-{index}" in existing_slugs:
        index += 1
    return f"{base_slug}-{index}"


def build_post(data: PostCreatePayload, existing_slugs: set[str]) -> Post:
    slug = ensure_unique_slug(slugify(data.title), existing_slugs)
    return Post(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        category_id=data.category_id,
    )


def extract_markdown_title(markdown: str) -> str:
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
    return {
        "filename": f"{post.slug}.md",
        "markdown": f"# {post.title}\n\n{post.content}",
    }


def _build_admin_post_list_query(category_id: int | None = None, tag_id: int | None = None):
    stmt = select(Post).order_by(Post.created_at.desc())
    if category_id is not None:
        stmt = stmt.where(Post.category_id == category_id)
    if tag_id is not None:
        stmt = stmt.where(Post.tags.any(Tag.id == tag_id))
    return stmt


def build_post_create_payload(
    db: Session,
    *,
    title: str,
    summary: str | None,
    content: str,
    category_id: int | None,
    tag_ids: list[int],
) -> tuple[PostCreatePayload, list[Tag]]:
    data = PostCreatePayload(
        title=title,
        summary=summary,
        content=content,
        category_id=resolve_category_id(db, category_id),
        tag_ids=tag_ids,
    )
    tags = get_tags_by_ids(db, data.tag_ids) if data.tag_ids else []
    return data, tags


def build_post_from_import_markdown(
    db: Session,
    payload: ImportMarkdownRequest,
) -> tuple[PostCreatePayload, list[Tag]]:
    return build_post_create_payload(
        db,
        title=extract_markdown_title(payload.markdown),
        summary=None,
        content=payload.markdown,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )


def create_post(db: Session, data: PostCreatePayload, tags: list[Tag]) -> Post:
    existing_slugs = set(db.execute(select(Post.slug)).scalars().all())
    post = build_post(data, existing_slugs=existing_slugs)
    if tags:
        post.tags = tags
    return post


def update_post(post: Post, data: PostCreatePayload, tags: list[Tag]) -> Post:
    post.title = data.title
    post.summary = data.summary
    post.content = data.content
    post.category_id = data.category_id
    post.tags = tags
    return post


def publish_post(post: Post) -> Post:
    post.published_at = datetime.now(timezone.utc)
    return post


def unpublish_post(post: Post) -> Post:
    post.published_at = None
    return post


def list_published_posts(
    db: Session, page: int = 1, page_size: int = 20
) -> tuple[list[Post], int]:
    """分页查询已发布文章"""
    base = select(Post).where(Post.published_at.is_not(None))
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar() or 0
    posts = list(
        db.execute(
            base.order_by(Post.published_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).scalars().all()
    )
    return posts, total


def get_post_by_slug(db: Session, slug: str) -> Post | None:
    stmt = select(Post).where(Post.slug == slug)
    return db.execute(stmt).scalar_one_or_none()


class PostNotFoundError(Exception):
    """文章不存在时抛出。"""
    pass


def get_post_or_raise(db: Session, post_id: int) -> Post:
    """根据 ID 获取文章，不存在则抛出 PostNotFoundError。"""
    post = db.get(Post, post_id)
    if not post:
        raise PostNotFoundError()
    return post


def save_new_post(db: Session, data: PostCreatePayload, tags: list[Tag]) -> Post:
    """创建新文章并持久化，触发 post.created 事件。"""
    post = create_post(db, data, tags)
    db.add(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.created", {"post_id": post.id, "slug": post.slug})
    return post


def save_post_update(db: Session, post: Post, data: PostCreatePayload, tags: list[Tag]) -> Post:
    """更新文章并持久化，触发 post.updated 事件。"""
    update_post(post, data, tags)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.updated", {"post_id": post.id, "slug": post.slug})
    return post


def save_publish(db: Session, post: Post) -> Post:
    """发布文章并持久化，触发 post.published 事件。"""
    publish_post(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.published", {"post_id": post.id, "slug": post.slug})
    return post


def save_unpublish(db: Session, post: Post) -> Post:
    """取消发布文章并持久化，触发 post.unpublished 事件。"""
    unpublish_post(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.unpublished", {"post_id": post.id, "slug": post.slug})
    return post


def list_admin_posts(
    db: Session,
    category_id: int | None = None,
    tag_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Post], int]:
    """后台文章列表查询，支持分类和标签筛选，带分页"""
    stmt = _build_admin_post_list_query(category_id, tag_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    posts = list(
        db.execute(
            stmt.offset((page - 1) * page_size).limit(page_size)
        ).scalars().all()
    )
    return posts, total


def delete_post(db: Session, post: Post) -> None:
    """删除文章并触发 post.deleted 事件"""
    post_id, slug = post.id, post.slug
    db.delete(post)
    db.commit()
    hook_bus.emit("post.deleted", {"post_id": post_id, "slug": slug})