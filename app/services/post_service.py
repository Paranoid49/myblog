import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.hook_bus import hook_bus
from app.models import Category, Post, Tag
from app.schemas.post import ImportMarkdownRequest
from app.services.markdown_service import extract_markdown_title
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


def _build_admin_post_list_query(category_id: int | None = None, tag_id: int | None = None) -> Select:
    """构建后台文章列表查询语句，支持分类和标签筛选。"""
    stmt = select(Post).options(selectinload(Post.category), selectinload(Post.tags)).order_by(Post.created_at.desc())
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
    """构建文章创建/更新的内部数据对象，同时解析分类和标签。"""
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
    """从导入的 Markdown 内容构建文章创建数据，标题自动从内容中提取。"""
    return build_post_create_payload(
        db,
        title=extract_markdown_title(payload.markdown),
        summary=None,
        content=payload.markdown,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
    )


def _slug_exists(db: Session, slug: str) -> bool:
    """检查 slug 是否已存在"""
    return db.execute(select(Post.id).where(Post.slug == slug).limit(1)).first() is not None


def create_post(db: Session, data: PostCreatePayload, tags: list[Tag]) -> Post:
    """创建 Post 实例并关联标签，slug 通过逐条查询数据库去重。"""
    base_slug = slugify(data.title)
    slug = base_slug
    index = 2
    while _slug_exists(db, slug):
        slug = f"{base_slug}-{index}"
        index += 1
    post = Post(
        title=data.title,
        slug=slug,
        summary=data.summary,
        content=data.content,
        category_id=data.category_id,
    )
    if tags:
        post.tags = tags
    return post


def update_post(post: Post, data: PostCreatePayload, tags: list[Tag]) -> Post:
    """用新数据更新文章字段和标签关联。"""
    post.title = data.title
    post.summary = data.summary
    post.content = data.content
    post.category_id = data.category_id
    post.tags = tags
    return post


def publish_post(post: Post) -> Post:
    """设置文章发布时间为当前 UTC 时间。"""
    post.published_at = datetime.now(UTC)
    return post


def unpublish_post(post: Post) -> Post:
    """清除文章发布时间，将其恢复为草稿状态。"""
    post.published_at = None
    return post


def list_published_posts(db: Session, page: int = 1, page_size: int = 20) -> tuple[list[Post], int]:
    """分页查询已发布文章"""
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    base = (
        select(Post)
        .options(selectinload(Post.category), selectinload(Post.tags))
        .where(Post.published_at.is_not(None))
    )
    total = db.execute(select(func.count()).select_from(base.subquery())).scalar() or 0
    posts = list(
        db.execute(base.order_by(Post.published_at.desc()).offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return posts, total


def get_post_by_slug(db: Session, slug: str) -> Post | None:
    """根据 slug 查询文章，不存在返回 None。预加载 category 和 tags 避免 N+1 查询。"""
    stmt = select(Post).options(selectinload(Post.category), selectinload(Post.tags)).where(Post.slug == slug)
    return db.execute(stmt).scalar_one_or_none()


def save_new_post(db: Session, data: PostCreatePayload, tags: list[Tag]) -> Post:
    """创建新文章并持久化，触发 post.created 事件。"""
    post = create_post(db, data, tags)
    try:
        db.add(post)
        db.commit()
    except IntegrityError:
        db.rollback()
        # slug 唯一约束冲突，用时间戳后缀重新生成
        post.slug = f"{post.slug}-{uuid.uuid4().hex[:8]}"
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
    page = max(1, page)
    page_size = max(1, min(page_size, 100))
    stmt = _build_admin_post_list_query(category_id, tag_id)
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    posts = list(db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all())
    return posts, total


def delete_post(db: Session, post: Post) -> None:
    """删除文章并触发 post.deleted 事件"""
    post_id, slug = post.id, post.slug
    db.delete(post)
    db.commit()
    hook_bus.emit("post.deleted", {"post_id": post_id, "slug": slug})
