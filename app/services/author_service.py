"""作者资料业务服务。"""

from sqlalchemy.orm import Session

from app.models.site_settings import SiteSettings


def update_author(
    db: Session,
    settings: SiteSettings,
    *,
    name: str,
    bio: str,
    email: str,
    avatar: str,
    link: str,
) -> SiteSettings:
    """更新作者资料并持久化。"""
    settings.author_name = name
    settings.author_bio = bio
    settings.author_email = email
    settings.author_avatar = avatar
    settings.author_link = link
    db.commit()
    db.refresh(settings)
    return settings
