import importlib


def load_extensions(module_paths: str | None) -> list[str]:
    if not module_paths:
        return []

    loaded: list[str] = []
    for raw_path in module_paths.split(","):
        module_path = raw_path.strip()
        if not module_path:
            continue
        importlib.import_module(module_path)
        loaded.append(module_path)
    return loaded
