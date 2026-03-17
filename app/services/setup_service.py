from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from app.models import SiteSettings, User
from app.services.auth_service import build_admin_user


class SetupAlreadyInitializedError(Exception):
    pass


REQUIRED_TABLES = {"users", "site_settings"}

# 内存缓存：初始化完成后设为 True，避免重复查询数据库
_initialized_cache: bool | None = None


def _has_required_tables(db: Session) -> bool:
    inspector = inspect(db.bind)
    return REQUIRED_TABLES.issubset(set(inspector.get_table_names()))


def is_initialized(db: Session) -> bool:
    """检查站点是否已完成初始化（存在管理员和站点设置）。"""
    global _initialized_cache
    if _initialized_cache is True:
        return True

    if not _has_required_tables(db):
        return False

    has_site_settings = db.execute(select(SiteSettings.id).limit(1)).first() is not None
    has_admin = db.execute(select(User.id).limit(1)).first() is not None
    result = has_site_settings and has_admin

    if result:
        _initialized_cache = True

    return result


def is_cache_initialized() -> bool:
    """检查初始化状态缓存是否命中（不查数据库）"""
    return _initialized_cache is True


def clear_initialized_cache() -> None:
    """清除初始化状态缓存（用于测试或数据库重置）"""
    global _initialized_cache
    _initialized_cache = None


def get_site_settings(db: Session) -> SiteSettings | None:
    """获取站点设置，表不存在或无数据时返回 None。"""
    # 初始化完成后跳过 inspect 检查，直接查询
    if _initialized_cache is not True and not _has_required_tables(db):
        return None
    return db.execute(select(SiteSettings)).scalar_one_or_none()


def initialize_site(db: Session, blog_title: str, username: str, password: str) -> User:
    """执行站点初始化：创建站点设置和管理员账户。"""
    global _initialized_cache

    if is_initialized(db):
        raise SetupAlreadyInitializedError()

    # 防御性检查：确保 SiteSettings 表中没有已有记录
    existing = db.execute(select(SiteSettings).limit(1)).scalar_one_or_none()
    if existing:
        raise SetupAlreadyInitializedError()

    site_settings = SiteSettings(blog_title=blog_title)
    user = build_admin_user(username, password)
    db.add(site_settings)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 初始化完成，设置缓存
    _initialized_cache = True

    return user
