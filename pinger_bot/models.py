"""DB models for the project."""
import dataclasses
import datetime
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sqlalchemy_asyncio
import sqlalchemy.orm as sqlalchemy_orm
import sqlalchemy.sql as sql
import structlog.stdlib as structlog

import pinger_bot.config as config

log = structlog.get_logger()
_ = config.gettext
Base = sqlalchemy_orm.declarative_base()
"""``Base`` object for all models.

.. seealso:: `<https://docs.sqlalchemy.org/en/14/orm/mapping_api.html#sqlalchemy.orm.declarative_base>`_
"""


# We ignore assign types because we assign column classes to built-in types. in runtime SQLAlchemy return built-in types
class Server(Base):  # type: ignore[valid-type,misc]
    """A server model. Used to store the server, that was added to bot."""

    __tablename__ = "pb_servers"

    id: int = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)  # type: ignore[assignment]
    """Unique ID of the server, primary key."""

    host: str = sqlalchemy.Column(sqlalchemy.String(256), nullable=False)  # type: ignore[assignment]
    """Hostname of the server, can be number IP or domain. Always without port."""
    port: int = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)  # type: ignore[assignment]
    """Port of the server."""
    max: int = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)  # type: ignore[assignment]
    """Max players on the server."""
    alias: typing.Optional[str] = sqlalchemy.Column(sqlalchemy.String(256), unique=True)  # type: ignore[assignment]
    """Alias of the server. Can be used as IP of the server."""
    owner: int = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)  # type: ignore[assignment]
    """Owner's Discord ID of the server."""

    __table_args__ = (sqlalchemy.UniqueConstraint("host", "port", name="ip"),)
    """Unique constraint for host and port."""


class Ping(Base):  # type: ignore[valid-type,misc]
    """Represents a single ping record in DB."""

    __tablename__ = "pb_pings"

    id: int = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.Identity(), primary_key=True)  # type: ignore[assignment]
    """Unique ID of the ping, primary key."""

    host: str = sqlalchemy.Column(sqlalchemy.ForeignKey(Server.host, name="server_host_to_ping_host"), nullable=False)  # type: ignore[assignment]
    """Host of the server, for which ping was made. This is a foreign key constraint."""
    port: int = sqlalchemy.Column(sqlalchemy.ForeignKey(Server.port, name="server_port_to_ping_port"), nullable=False)  # type: ignore[assignment,arg-type]
    """Port of the server, for which ping was made. This is a foreign key constraint."""
    time: datetime.datetime = sqlalchemy.Column(sqlalchemy.DateTime, server_default=sql.func.now(), nullable=False)  # type: ignore[assignment]
    """Time of the ping. Default to current time."""
    players: int = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # type: ignore[assignment]
    """Players online in moment of the ping."""

    __mapper_args__ = {"eager_defaults": True}
    """Some magic to make eager loading work.

    .. seealso:: `<https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-orm>`_
    """


@dataclasses.dataclass(frozen=True)
class Database:
    """Some cached info about database."""

    log.info(_("Starting DB..."))
    engine: sqlalchemy_asyncio.AsyncEngine = sqlalchemy_asyncio.create_async_engine(
        config.config.db_uri, echo=config.config.debug
    )
    """Async engine of the Database."""
    session: typing.Callable[[], typing.AsyncContextManager[sqlalchemy_asyncio.AsyncSession]] = sqlalchemy_orm.sessionmaker(
        engine, expire_on_commit=False, class_=sqlalchemy_asyncio.AsyncSession
    )
    """Async session of the Database."""


db = Database()
"""Initialized :py:class:`.Database` object."""
