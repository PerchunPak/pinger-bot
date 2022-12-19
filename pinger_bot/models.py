"""DB models for the project."""
import dataclasses
import datetime
import functools
import typing

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import sql
from sqlalchemy.ext import asyncio as sqlalchemy_asyncio
from structlog import stdlib as structlog

from pinger_bot import config
from pinger_bot.config import gettext as _

log = structlog.get_logger()
Base = sqlalchemy.orm.declarative_base()
"""``Base`` object for all models.

.. seealso:: `<https://docs.sqlalchemy.org/en/14/orm/mapping_api.html#sqlalchemy.orm.declarative_base>`_
"""


# We ignore assign types because we assign column classes to built-in types. in runtime SQLAlchemy return built-in types
@dataclasses.dataclass
class Server(Base):  # type: ignore[valid-type,misc]
    """A server model. Used to store the server, that was added to bot."""

    __tablename__ = "pb_servers"

    id: int = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)  # type: ignore[assignment]
    """Unique ID of the server, primary key."""

    host: str = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)  # type: ignore[assignment]
    """Hostname of the server, can be number IP or domain. Always without port."""
    port: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # type: ignore[assignment]
    """Port of the server."""
    max: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # type: ignore[assignment]
    """Max players on the server."""
    alias: typing.Optional[str] = sqlalchemy.Column(sqlalchemy.String(256), unique=True)  # type: ignore[assignment]
    """Alias of the server. Can be used as IP of the server."""
    owner: int = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)  # type: ignore[assignment]
    """Owner's Discord ID of the server."""

    __table_args__ = (sqlalchemy.UniqueConstraint("host", "port", name="ip"),)
    """Unique constraint for host and port."""


@dataclasses.dataclass
class Ping(Base):  # type: ignore[valid-type,misc]
    """Represents a single ping record in DB."""

    __tablename__ = "pb_pings"

    id: int = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)  # type: ignore[assignment]
    """Unique ID of the ping, primary key."""

    host: str = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)  # type: ignore[assignment]
    """Host of the server, for which ping was made. This is a foreign key constraint."""
    port: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # type: ignore[assignment]
    """Port of the server, for which ping was made. This is a foreign key constraint."""
    time: datetime.datetime = sqlalchemy.Column(sqlalchemy.DateTime, server_default=sql.func.now(), nullable=False)  # type: ignore[assignment]
    """Time of the ping. Default to current time."""
    players: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # type: ignore[assignment]
    """Players online in moment of the ping."""

    __mapper_args__ = {"eager_defaults": True}
    """Some magic to make eager loading work.

    .. seealso:: `<https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-orm>`_
    """
    __table_args__ = (
        sqlalchemy.ForeignKeyConstraint(
            ["host", "port"], ["pb_servers.host", "pb_servers.port"], name="ping_to_server"
        ),
    )
    """Define Foreign Key Constraint to associate :attr:`pb_pings.host <.Ping.host>` and \
    :attr:`pb_pings.port <.Server.port>` to :attr:`pb_pings.host <.Ping.host>` and \
    :attr:`pb_pings.port <.Server.port>`."""


class Database:
    """Some cached info about database."""

    @functools.cached_property
    def engine(self) -> sqlalchemy_asyncio.AsyncEngine:
        """Async engine of the Database."""
        log.info(_("Starting DB..."))
        return sqlalchemy_asyncio.create_async_engine(config.config.db_uri, echo=config.config.debug)

    @functools.cached_property
    def session(self) -> typing.Callable[[], typing.AsyncContextManager[sqlalchemy_asyncio.AsyncSession]]:
        """Async session of the Database."""
        return sqlalchemy.orm.sessionmaker(self.engine, expire_on_commit=False, class_=sqlalchemy_asyncio.AsyncSession)


db = Database()
"""Initialized :py:class:`.Database` object."""
