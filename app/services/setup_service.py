from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import SiteSettings, User
from app.services.auth_service import build_admin_user


class SetupAlreadyInitializedError(Exception):
    pass


REQUIRED_TABLES = {"users", "site_settings"}


def _has_required_tables(db: Session) -> bool:
    inspector = inspect(db.bind)
    return REQUIRED_TABLES.issubset(set(inspector.get_table_names()))


def is_initialized(db: Session) -> bool:
    if not _has_required_tables(db):
        return False

    has_site_settings = db.execute(select(SiteSettings.id).limit(1)).first() is not None
    has_admin = db.execute(select(User.id).limit(1)).first() is not None
    return has_site_settings and has_admin


def get_site_settings(db: Session) -> SiteSettings | None:
    if not _has_required_tables(db):
        return None
    return db.execute(select(SiteSettings)).scalar_one_or_none()


def initialize_site(db: Session, blog_title: str, username: str, password: str) -> User:
    if is_initialized(db):
        raise SetupAlreadyInitializedError()

    site_settings = SiteSettings(blog_title=blog_title)
    user = build_admin_user(username, password)
    db.add(site_settings)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
