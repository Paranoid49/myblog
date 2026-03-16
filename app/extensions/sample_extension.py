import logging

from app.core.hook_bus import HookEvent, hook_bus

logger = logging.getLogger(__name__)


def _on_post_published(event: HookEvent) -> None:
    """文章发布时记录日志"""
    post_id = event.payload.get("post_id")
    slug = event.payload.get("slug")
    logger.info("文章已发布: id=%s, slug=%s", post_id, slug)


def _on_post_deleted(event: HookEvent) -> None:
    """文章删除时记录日志"""
    post_id = event.payload.get("post_id")
    logger.info("文章已删除: id=%s", post_id)


def setup() -> None:
    """注册事件监听器"""
    hook_bus.subscribe("post.published", _on_post_published)
    hook_bus.subscribe("post.deleted", _on_post_deleted)


setup()
