import re

from pypinyin import Style, lazy_pinyin
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Post, Tag
from app.schemas.post import PostCreate


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


def update_post(post: Post, data: PostCreate, tags: list[Tag]) -> Post:
    post.title = data.title
    post.summary = data.summary
    post.content = data.content
    post.category_id = data.category_id
    post.tags = tags
    return post


def list_published_posts(db: Session) -> list[Post]:
    stmt = select(Post).order_by(Post.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def get_post_by_slug(db: Session, slug: str) -> Post | None:
    stmt = select(Post).where(Post.slug == slug)
    return db.execute(stmt).scalar_one_or_none()


