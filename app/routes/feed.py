"""RSS Feed 生成模块。"""

import time
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.post_service import list_published_posts
from app.services.setup_service import get_site_settings

router = APIRouter(tags=["feed"])

# RSS 内存缓存：缓存生成的 XML 及过期时间（5 分钟）
_feed_cache: dict = {"xml": None, "expires": 0}


@router.get("/feed.xml", include_in_schema=False)
def rss_feed(db: Session = Depends(get_db)) -> Response:
    """生成 RSS 2.0 Feed（5 分钟缓存）"""
    now = time.time()
    if _feed_cache["xml"] and now < _feed_cache["expires"]:
        return Response(content=_feed_cache["xml"], media_type="application/rss+xml")

    posts, _ = list_published_posts(db)
    site = get_site_settings(db)
    blog_title = site.blog_title if site else "myblog"
    items = "".join(
        f"""<item>
            <title>{escape(p.title)}</title>
            <link>/posts/{escape(p.slug)}</link>
            <description>{escape(p.summary or "")}</description>
            <pubDate>{p.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
        </item>"""
        for p in posts
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{escape(blog_title)}</title>
        <link>/</link>
        <description>技术博客</description>
        {items}
    </channel>
</rss>"""

    # 写入缓存，5 分钟有效期
    _feed_cache["xml"] = xml
    _feed_cache["expires"] = now + 300
    return Response(content=xml, media_type="application/rss+xml")
