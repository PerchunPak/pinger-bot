"""Use Integer type in some fields, instead of SmallInteger.

Revision ID: 461c3a5c3ebe
Revises: 0e85daa02553
Create Date: 2022-08-22 20:25:53.897761

"""
import typing

import alembic.op as op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "461c3a5c3ebe"
down_revision: typing.Optional[str] = "0e85daa02553"
branch_labels: typing.Optional[str] = None
depends_on: typing.Optional[str] = None


def upgrade() -> None:
    """Upgrade actions that must be performed when upgrading the database to this revision."""
    with op.batch_alter_table("pb_servers", schema=None) as batch_op:
        batch_op.alter_column(
            "port",
            type_=sa.Integer(),
            existing_type=sa.SmallInteger(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "max",
            type_=sa.Integer(),
            existing_type=sa.SmallInteger(),
            existing_nullable=False,
        )

    with op.batch_alter_table("pb_pings", schema=None) as batch_op:
        batch_op.alter_column(
            "port",
            type_=sa.Integer(),
            existing_type=sa.SmallInteger(),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade actions that must be performed when downgrading the database from this revision."""
    with op.batch_alter_table("pb_servers", schema=None) as batch_op:
        batch_op.alter_column(
            "port",
            type_=sa.SmallInteger(),
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "max",
            type_=sa.SmallInteger(),
            existing_type=sa.Integer(),
            existing_nullable=False,
        )

    with op.batch_alter_table("pb_pings", schema=None) as batch_op:
        batch_op.alter_column(
            "port",
            type_=sa.SmallInteger(),
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
