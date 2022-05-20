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


class Server(Base):  # type: ignore[valid-type,misc]
    """A server model. Used to store the server, that was added to bot."""

    __tablename__ = "pb_servers"

    id = Column(Integer, Identity(), primary_key=True)

    host = Column(String(256), nullable=False)
    port = Column(SmallInteger, nullable=False)
    max = Column(SmallInteger, nullable=False)
    alias = Column(String(256), unique=True, nullable=False)
    owner = Column(BigInteger, nullable=False)

    __table_args__ = (UniqueConstraint("host", "port", name="ip"),)


class Ping(Base):  # type: ignore[valid-type,misc]
    """Represents a single ping record in DB."""

    __tablename__ = "pb_pings"

    id = Column(Integer, Identity(), primary_key=True)

    host = Column(ForeignKey(Server.host, name="server_host_to_ping_host"), nullable=False)
    port = Column(ForeignKey(Server.port, name="server_port_to_ping_port"), nullable=False)
    time = Column(DateTime, nullable=False)
    players = Column(Integer, nullable=False)

    __mapper_args__ = {"eager_defaults": True}


@dataclass(frozen=True)
class Database:
    """Some cached info about database."""

    log.info(_("Starting DB engine..."))
    engine: AsyncEngine = create_async_engine(config.db_uri, echo=config.debug)
    log.debug(_("Starting DB session..."))
    session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


db = Database()
