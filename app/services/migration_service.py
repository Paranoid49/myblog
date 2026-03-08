from pathlib import Path

from alembic import command
from alembic.config import Config


def upgrade_database() -> None:
    config = Config(str(Path("alembic.ini")))
    command.upgrade(config, "head")
