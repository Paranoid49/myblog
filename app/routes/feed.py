"""RSS Feed 生成模块。"""

from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.post_service import list_published_posts

router = APIRouter(tags=["feed"])


@router.get("/feed.xml", include_in_schema=False)
def rss_feed(db: Session = Depends(get_db)) -> Response:
    """生成 RSS 2.0 Feed"""
    posts, _ = list_published_posts(db)
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
        <title>myblog</title>
        <link>/</link>
        <description>技术博客</description>
        {items}
    </channel>
</rss>"""
    return Response(content=xml, media_type="application/rss+xml")
