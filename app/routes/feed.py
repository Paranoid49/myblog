"""RSS Feed 生成模块。"""

import time
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.post_service import list_published_posts
from app.services.setup_service import get_site_settings

router = APIRouter(tags=["feed"])

# RSS 内存缓存：按 base_url 分别缓存，避免不同域名访问时 URL 不一致
_feed_cache: dict = {}


@router.get("/feed.xml", include_in_schema=False)
def rss_feed(request: Request, db: Session = Depends(get_db)) -> Response:
    """生成 RSS 2.0 Feed（5 分钟内存缓存，按 base_url 区分）"""
    base_url = str(request.base_url).rstrip("/")
    cached = _feed_cache.get(base_url)
    if cached and time.time() < cached["expires"]:
        return Response(content=cached["xml"], media_type="application/rss+xml")

    # 缓存过期或不存在，重新生成 XML
    posts, _ = list_published_posts(db)
    site = get_site_settings(db)
    blog_title = site.blog_title if site else "myblog"
    items = "".join(
        f"""<item>
            <title>{escape(p.title)}</title>
            <link>{base_url}/posts/{escape(p.slug)}</link>
            <description>{escape(p.summary or "")}</description>
            <pubDate>{p.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
            <guid isPermaLink="true">{base_url}/posts/{escape(p.slug)}</guid>
        </item>"""
        for p in posts
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{escape(blog_title)}</title>
        <link>{base_url}/</link>
        <description>技术博客</description>
        {items}
    </channel>
</rss>"""

    _feed_cache[base_url] = {"xml": xml, "expires": time.time() + 300}

    return Response(content=xml, media_type="application/rss+xml")
