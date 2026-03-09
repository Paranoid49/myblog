from app.core.hook_bus import HookEvent, hook_bus


def _on_post_published(event: HookEvent) -> None:
    _ = event.payload.get("post_id")


def setup() -> None:
    hook_bus.subscribe("post.published", _on_post_published)


setup()
