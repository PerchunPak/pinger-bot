"""Make alias nullable.

Revision ID: 3c528416c556
Revises: 14f37c9b7479
Create Date: 2022-05-23 22:04:45.728189

"""
import typing

import alembic.op as op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3c528416c556"
down_revision: typing.Optional[str] = "14f37c9b7479"
branch_labels: typing.Optional[str] = None
depends_on: typing.Optional[str] = None


def upgrade() -> None:
    """Upgrade actions that must be performed when upgrading the database to this revision."""
    with op.batch_alter_table("pb_servers", schema=None) as batch_op:
        batch_op.alter_column("alias", existing_type=sa.String(length=256), nullable=True)


def downgrade() -> None:
    """Downgrade actions that must be performed when downgrading the database from this revision."""
    with op.batch_alter_table("pb_servers", schema=None) as batch_op:
        batch_op.alter_column("alias", existing_type=sa.String(length=256), nullable=False)
