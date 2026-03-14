import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from pypinyin import Style, lazy_pinyin

from app.models import Post, Tag
from app.schemas.post import ImportMarkdownRequest, PostCreate


def _normalize_chunks(value: str) -> list[str]:
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
    chunks = _normalize_chunks(value)
    slug = "-".join(chunk for chunk in chunks if chunk)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "post"


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


def build_admin_post_list_query(category_id: int | None = None, tag_id: int | None = None):
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
    from app.services.admin_post_service import get_tags_by_ids, resolve_category_id

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


