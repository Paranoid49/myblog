import importlib
import logging

logger = logging.getLogger(__name__)


def load_extensions(module_paths: str | None) -> list[str]:
    if not module_paths:
        return []

    loaded: list[str] = []
    for raw_path in module_paths.split(","):
        module_path = raw_path.strip()
        if not module_path:
            continue
        try:
            importlib.import_module(module_path)
            loaded.append(module_path)
        except Exception:
            logger.exception("failed to load extension '%s'", module_path)
    return loaded
