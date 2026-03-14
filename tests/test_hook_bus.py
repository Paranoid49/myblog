from app.core.hook_bus import HookBus


def test_hook_bus_emits_to_subscribers() -> None:
    bus = HookBus()
    called = []

    def handler(event):
        called.append((event.name, event.payload.get("value")))

    bus.subscribe("post.created", handler)
    bus.emit("post.created", {"value": 1})

    assert called == [("post.created", 1)]


def test_hook_bus_calls_multiple_handlers_in_subscription_order() -> None:
    bus = HookBus()
    called = []

    def first_handler(event):
        called.append(("first", event.payload.get("value")))

    def second_handler(event):
        called.append(("second", event.payload.get("value")))

    bus.subscribe("post.created", first_handler)
    bus.subscribe("post.created", second_handler)
    bus.emit("post.created", {"value": 3})

    assert called == [("first", 3), ("second", 3)]


def test_hook_bus_ignores_unknown_event() -> None:
    bus = HookBus()
    bus.emit("post.created", {"value": 1})


def test_hook_bus_isolates_handler_exceptions() -> None:
    bus = HookBus()
    called = []

    def bad_handler(_event):
        raise RuntimeError("boom")

    def good_handler(event):
        called.append(event.payload.get("value"))

    bus.subscribe("post.created", bad_handler)
    bus.subscribe("post.created", good_handler)

    bus.emit("post.created", {"value": 2})

    assert called == [2]
