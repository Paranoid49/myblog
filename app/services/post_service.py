from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.hook_bus import hook_bus
from app.models import Post, Tag
from app.schemas.post import ImportMarkdownRequest, PostCreate
from app.services.admin_post_service import get_tags_by_ids, resolve_category_id
from app.utils.text import slugify


def ensure_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    if base_slug not in existing_slugs:
        return base_slug

    index = 2
    while f"{base_slug}-{index}" in existing_slugs:
        index += 1
    return f"{base_slug}-{index}"


def build_post(data: PostCreate, existing_slugs: set[str]) -> Post:
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
) -> tuple[PostCreate, list[Tag]]:
    data = PostCreate(
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
) -> tuple[PostCreate, list[Tag]]:
    return build_post_create_payload(
        db,
        title=extract_markdown_title(payload.markdown),
        summary=None,
        content=payload.markdown,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )


def create_post(db: Session, data: PostCreate, tags: list[Tag]) -> Post:
    existing_slugs = set(db.execute(select(Post.slug)).scalars().all())
    post = build_post(data, existing_slugs=existing_slugs)
    if tags:
        post.tags = tags
    return post


def update_post(post: Post, data: PostCreate, tags: list[Tag]) -> Post:
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


def list_published_posts(db: Session) -> list[Post]:
    stmt = select(Post).where(Post.published_at.is_not(None)).order_by(Post.published_at.desc())
    return list(db.execute(stmt).scalars().all())


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


def save_new_post(db: Session, data: PostCreate, tags: list[Tag]) -> Post:
    """创建新文章并持久化，触发 post.created 事件。"""
    post = create_post(db, data, tags)
    db.add(post)
    db.commit()
    db.refresh(post)
    hook_bus.emit("post.created", {"post_id": post.id, "slug": post.slug})
    return post


def save_post_update(db: Session, post: Post, data: PostCreate, tags: list[Tag]) -> Post:
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


def list_admin_posts(db: Session, category_id: int | None = None, tag_id: int | None = None) -> list[Post]:
    """后台文章列表查询，支持按分类和标签筛选。"""
    return list(db.execute(_build_admin_post_list_query(category_id, tag_id)).scalars().all())