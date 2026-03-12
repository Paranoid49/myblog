from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Tag
from app.services.post_service import slugify


def resolve_category_id(db: Session, category_id: int | None) -> int:
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


def get_tags_by_ids(db: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    return list(db.execute(select(Tag).where(Tag.id.in_(tag_ids))).scalars().all())


def category_exists_by_name(db: Session, name: str) -> bool:
    return db.execute(select(Category.id).where(Category.slug == slugify(name))).first() is not None


def tag_exists_by_name(db: Session, name: str) -> bool:
    return db.execute(select(Tag.id).where(Tag.slug == slugify(name))).first() is not None
