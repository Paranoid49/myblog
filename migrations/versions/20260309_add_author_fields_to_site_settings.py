from alembic import op
import sqlalchemy as sa


revision = "20260309_add_author_fields"
down_revision = "20260308_add_site_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_settings", sa.Column("author_name", sa.String(length=100), nullable=False, server_default="admin"))
    op.add_column("site_settings", sa.Column("author_bio", sa.Text(), nullable=False, server_default=""))
    op.add_column("site_settings", sa.Column("author_email", sa.String(length=200), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("site_settings", "author_email")
    op.drop_column("site_settings", "author_bio")
    op.drop_column("site_settings", "author_name")
