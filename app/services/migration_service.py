from alembic import command
from alembic.config import Config

from app.core.config import PROJECT_ROOT


def upgrade_database() -> None:
    """执行 Alembic 数据库迁移，将数据库升级到最新版本。"""
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    command.upgrade(config, "head")
