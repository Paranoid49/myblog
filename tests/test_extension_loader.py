import sys

import pytest

from app.core.extension_loader import load_extensions
from app.core.hook_bus import hook_bus


def test_load_extensions_returns_empty_for_blank() -> None:
    assert load_extensions("") == []


def test_load_extensions_skips_blank_items() -> None:
    loaded = load_extensions(" app.extensions.sample_extension, , ")
    assert loaded == ["app.extensions.sample_extension"]


def test_load_extensions_imports_sample_extension() -> None:
    hook_bus._handlers.clear()
    sys.modules.pop("app.extensions.sample_extension", None)

    loaded = load_extensions("app.extensions.sample_extension")

    assert loaded == ["app.extensions.sample_extension"]
    assert "post.published" in hook_bus._handlers
    assert len(hook_bus._handlers["post.published"]) >= 1


def test_load_extensions_raises_for_missing_module() -> None:
    with pytest.raises(ModuleNotFoundError):
        load_extensions("app.extensions.not_exists")
