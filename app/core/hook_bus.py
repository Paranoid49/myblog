import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HookEvent:
    name: str
    payload: dict[str, Any]


HookHandler = Callable[[HookEvent], None]


class HookBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[HookHandler]] = {}

    def subscribe(self, event_name: str, handler: HookHandler) -> None:
        self._handlers.setdefault(event_name, []).append(handler)

    def emit(self, event_name: str, payload: dict[str, Any]) -> None:
        event = HookEvent(name=event_name, payload=payload)
        for handler in self._handlers.get(event_name, []):
            try:
                handler(event)
            except Exception:
                logger.exception("hook handler failed for event '%s'", event_name)
                continue


hook_bus = HookBus()
