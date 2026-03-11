from alembic import op
import sqlalchemy as sa


revision = "20260311_add_author_avatar_and_link"
down_revision = "20260309_add_author_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_settings", sa.Column("author_avatar", sa.String(length=500), nullable=False, server_default=""))
    op.add_column("site_settings", sa.Column("author_link", sa.String(length=500), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("site_settings", "author_link")
    op.drop_column("site_settings", "author_avatar")
