"""${message}.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
import typing

import alembic.op as op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: typing.Optional[str] = ${repr(down_revision)}
branch_labels: typing.Optional[str] = ${repr(branch_labels)}
depends_on: typing.Optional[str] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade actions that must be performed when upgrading the database to this revision."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade actions that must be performed when downgrading the database from this revision."""
    ${downgrades if downgrades else "pass"}
