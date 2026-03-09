from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_title: Mapped[str] = mapped_column(String(200))
    author_name: Mapped[str] = mapped_column(String(100), default="admin", server_default="admin")
    author_bio: Mapped[str] = mapped_column(Text, default="", server_default="")
    author_email: Mapped[str] = mapped_column(String(200), default="", server_default="")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
