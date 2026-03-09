from app.core.extension_loader import load_extensions


def test_load_extensions_returns_empty_for_blank() -> None:
    assert load_extensions("") == []


def test_load_extensions_imports_sample_extension() -> None:
    loaded = load_extensions("app.extensions.sample_extension")
    assert loaded == ["app.extensions.sample_extension"]
