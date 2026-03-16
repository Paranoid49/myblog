import sys

from app.core.extension_loader import load_extensions
from app.core.hook_bus import hook_bus


def test_load_extensions_returns_empty_for_blank() -> None:
    assert load_extensions("") == ([], [])


def test_load_extensions_skips_blank_items() -> None:
    loaded, failed = load_extensions(" app.extensions.sample_extension, , ")
    assert loaded == ["app.extensions.sample_extension"]
    assert failed == []


def test_load_extensions_imports_sample_extension() -> None:
    hook_bus._handlers.clear()
    sys.modules.pop("app.extensions.sample_extension", None)

    loaded, failed = load_extensions("app.extensions.sample_extension")

    assert loaded == ["app.extensions.sample_extension"]
    assert failed == []
    assert "post.published" in hook_bus._handlers
    assert len(hook_bus._handlers["post.published"]) >= 1


def test_load_extensions_skips_missing_module() -> None:
    """加载不存在的模块时记录失败并返回失败列表。"""
    loaded, failed = load_extensions("app.extensions.not_exists")
    assert loaded == []
    assert failed == ["app.extensions.not_exists"]
