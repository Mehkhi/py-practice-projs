"""add status column backfill

Revision ID: 030829ba1a2f
Revises: 20240306_advanced_features
Create Date: 2025-11-20 05:51:20.176060

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "030829ba1a2f"
down_revision = "20240306_advanced_features"
branch_labels = None
depends_on = None

TABLE_NAME = "tasks"
COLUMN_NAME = "status"
INDEX_NAME = "ix_tasks_status"


def _table_state():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(TABLE_NAME)}
    indexes = {idx["name"] for idx in inspector.get_indexes(TABLE_NAME)}
    return columns, indexes


def upgrade():
    columns, indexes = _table_state()
    column_missing = COLUMN_NAME not in columns
    index_missing = INDEX_NAME not in indexes

    if column_missing or index_missing:
        with op.batch_alter_table(TABLE_NAME) as batch_op:
            if column_missing:
                batch_op.add_column(
                    sa.Column(
                        COLUMN_NAME,
                        sa.String(length=20),
                        nullable=False,
                        server_default="backlog",
                    )
                )
            if index_missing:
                batch_op.create_index(INDEX_NAME, [COLUMN_NAME])

    if column_missing:
        op.execute(
            sa.text(
                """
                UPDATE tasks
                SET status = CASE
                    WHEN completed = 1 THEN 'done'
                    ELSE 'backlog'
                END
                """
            )
        )
        op.execute(sa.text("UPDATE tasks SET status = 'backlog' WHERE status IS NULL"))


def downgrade():
    columns, indexes = _table_state()
    column_exists = COLUMN_NAME in columns
    index_exists = INDEX_NAME in indexes

    if column_exists or index_exists:
        with op.batch_alter_table(TABLE_NAME) as batch_op:
            if index_exists:
                batch_op.drop_index(INDEX_NAME)
            if column_exists:
                batch_op.drop_column(COLUMN_NAME)
