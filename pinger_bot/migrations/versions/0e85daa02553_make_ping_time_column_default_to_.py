"""Make Ping.time column default to current time.

Revision ID: 0e85daa02553
Revises: 3c528416c556
Create Date: 2022-05-29 12:23:17.093320

"""
from typing import Optional

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0e85daa02553"
down_revision: Optional[str] = "3c528416c556"
branch_labels: Optional[str] = None
depends_on: Optional[str] = None


def upgrade() -> None:
    """Upgrade actions that must be performed when upgrading the database to this revision."""
    with op.batch_alter_table("pb_pings", schema=None) as batch_op:
        batch_op.alter_column(
            "time",
            existing_type=sa.DateTime(),
            server_default=sa.sql.func.now(),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade actions that must be performed when downgrading the database from this revision."""
    with op.batch_alter_table("pb_pings", schema=None) as batch_op:
        batch_op.alter_column("time", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)
