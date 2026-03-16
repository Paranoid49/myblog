from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """验证用户凭据，成功返回用户对象，失败返回 None。"""
    stmt = select(User).where(User.username == username)
    user = db.execute(stmt).scalar_one_or_none()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def build_admin_user(username: str, password: str) -> User:
    """构建管理员用户实例，密码自动哈希处理。"""
    return User(username=username, password_hash=hash_password(password), is_active=True)
