"""DB models for the project."""
from dataclasses import dataclass

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from structlog.stdlib import get_logger

from pinger_bot.config import config
from pinger_bot.config import gettext as _

log = get_logger()
Base = declarative_base()
"""``Base`` object for all models.

.. seealso:: `<https://docs.sqlalchemy.org/en/14/orm/mapping_api.html#sqlalchemy.orm.declarative_base>`_
"""


class Server(Base):  # type: ignore[valid-type,misc]
    """A server model. Used to store the server, that was added to bot."""

    __tablename__ = "pb_servers"

    id = Column(Integer, Identity(), primary_key=True)
    """Unique ID of the server, primary key."""

    host = Column(String(256), nullable=False)
    """Hostname of the server, can be number IP or domain. Always without port."""
    port = Column(SmallInteger, nullable=False)
    """Port of the server."""
    max = Column(SmallInteger, nullable=False)
    """Max players on the server."""
    alias = Column(String(256), unique=True)
    """Alias of the server. Can be used as IP of the server."""
    owner = Column(BigInteger, nullable=False)
    """Owner's Discord ID of the server."""

    __table_args__ = (UniqueConstraint("host", "port", name="ip"),)
    """Unique constraint for host and port."""


class Ping(Base):  # type: ignore[valid-type,misc]
    """Represents a single ping record in DB."""

    __tablename__ = "pb_pings"

    id = Column(Integer, Identity(), primary_key=True)
    """Unique ID of the ping, primary key."""

    host = Column(ForeignKey(Server.host, name="server_host_to_ping_host"), nullable=False)
    """Host of the server, for which ping was made. This is a foreign key constraint."""
    port = Column(ForeignKey(Server.port, name="server_port_to_ping_port"), nullable=False)
    """Port of the server, for which ping was made. This is a foreign key constraint."""
    time = Column(DateTime, nullable=False)
    """Time of the ping."""
    players = Column(Integer, nullable=False)
    """Players online in moment of the ping."""

    __mapper_args__ = {"eager_defaults": True}
    """Some magic to make eager loading work.

    .. seealso:: `<https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#synopsis-orm>`_
    """


@dataclass(frozen=True)
class Database:
    """Some cached info about database."""

    log.info(_("Starting DB..."))
    engine: AsyncEngine = create_async_engine(config.db_uri, echo=config.debug)
    """Async engine of the Database."""
    session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    """Async session of the Database."""


db = Database()
"""Initialized :py:class:`.Database` object."""
