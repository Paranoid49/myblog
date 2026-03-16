import importlib
import logging

logger = logging.getLogger(__name__)


def load_extensions(module_paths: str | None) -> tuple[list[str], list[str]]:
    """加载扩展模块，返回 (成功列表, 失败列表)"""
    if not module_paths:
        return [], []

    loaded: list[str] = []
    failed: list[str] = []
    for raw_path in module_paths.split(","):
        module_path = raw_path.strip()
        if not module_path:
            continue
        try:
            importlib.import_module(module_path)
            loaded.append(module_path)
            logger.info("扩展加载成功: %s", module_path)
        except Exception:
            logger.exception("扩展加载失败: %s", module_path)
            failed.append(module_path)

    if failed:
        logger.warning("以下扩展加载失败: %s", ", ".join(failed))

    return loaded, failed
