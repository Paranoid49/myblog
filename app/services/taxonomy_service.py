from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Category, Tag


def list_taxonomy(db: Session) -> tuple[list[Category], list[Tag]]:
    categories = list(db.execute(select(Category).order_by(Category.name.asc())).scalars().all())
    tags = list(db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all())
    return categories, tags


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    stmt = select(Category).options(selectinload(Category.posts)).where(Category.slug == slug)
    return db.execute(stmt).scalar_one_or_none()


def get_tag_by_slug(db: Session, slug: str) -> Tag | None:
    stmt = select(Tag).options(selectinload(Tag.posts)).where(Tag.slug == slug)
    return db.execute(stmt).scalar_one_or_none()
