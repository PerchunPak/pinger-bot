"""API module with Minecraft Servers API."""
import asyncio
import dataclasses
import typing
from abc import ABC

import asyncache
import cachetools
import dns.asyncresolver
import dns.exception
import mcstatus
import sqlalchemy
from dns.rdatatype import RdataType as DNSRdataType
from structlog import stdlib as structlog

from pinger_bot import models
from pinger_bot.config import gettext as _

log = structlog.get_logger()

_Address_resolve_cache: cachetools.TTLCache = cachetools.TTLCache(128, 3600)  # type: ignore[type-arg]
"""Helper for tests, this used when you need to remove the cache."""


@dataclasses.dataclass
class Address:
    """Class for containing information about server address."""

    host: str
    """Host where server is, like ``127.0.0.1``."""
    port: int
    """Port of the server, example ``25565`` or ``19132``."""
    input_ip: str
    """Unparsed and unmodified IP, which was passed before everything."""
    alias: typing.Optional[str]
    """Alias of the server."""
    display_ip: str
    """Display IP of the server (:py:attr:`.alias`, if this unset - :py:attr:`.input_ip`)."""
    num_ip: str
    """Number IP of the server. Always with port. Example ``127.0.0.1:25565``."""
    _server: typing.Union[mcstatus.JavaServer, mcstatus.BedrockServer]
    """Private attribute with JavaServer or BedrockServer instance."""

    @classmethod
    @asyncache.cached(_Address_resolve_cache)
    async def resolve(cls, input_ip: str, *, java: bool) -> "Address":
        """Resolve IP or domain or alias to :py:class:`.Address` object.

        Args:
            input_ip: IP or domain or alias to resolve.
            java: If True, then :class:`mcstatus.JavaServer` will be used. Else - :class:`mcstatus.BedrockServer`.

        Returns:
            Resolved :py:class:`.Address` object.
        """
        log.debug("Address.resolve", input_ip=input_ip, java=java)
        ip_from_alias = await cls._get_ip_from_alias(input_ip)

        if ip_from_alias is not None:
            server = (
                await mcstatus.JavaServer.async_lookup(ip_from_alias)
                if java
                else mcstatus.BedrockServer.lookup(ip_from_alias)
            )
            return cls(
                host=server.address.host,
                port=server.address.port,
                input_ip=input_ip,
                alias=input_ip,
                display_ip=input_ip,
                num_ip=(await cls._get_number_ip(server.address.host)) + ":" + str(server.address.port),
                _server=server,
            )

        server = await mcstatus.JavaServer.async_lookup(input_ip) if java else mcstatus.BedrockServer.lookup(input_ip)

        num_ip_without_port, alias = await asyncio.gather(
            cls._get_number_ip(server.address.host), cls._get_alias_from_ip(server.address.host, server.address.port)
        )

        return cls(
            host=server.address.host,
            port=server.address.port,
            input_ip=input_ip,
            alias=alias,
            display_ip=alias if alias is not None else input_ip,
            num_ip=num_ip_without_port + ":" + str(server.address.port),
            _server=server,
        )

    @staticmethod
    async def _get_ip_from_alias(alias: str) -> typing.Optional[str]:
        """Get IP from alias.

        Args:
            alias: Alias to resolve.

        Returns:
            IP if alias was found, else None.
        """
        log.debug("Address._get_ip_from_alias", alias=alias)
        async with models.db.session() as session:
            server = await session.execute(
                sqlalchemy.select(models.Server.host, models.Server.port).where(models.Server.alias == alias)
            )
        row = server.first()

        log.debug("Address._get_ip_from_alias row", row=row)
        return str(row.host + ":" + str(row.port)) if row is not None else None

    @staticmethod
    async def _get_number_ip(input_ip: str) -> str:
        """Make query to DNS and get number IP.

        Args:
            input_ip: Domain to query.

        Returns:
            Number IP or input IP if resolving failed.
        """
        log.debug("Address._get_number_ip", input_ip=input_ip)
        try:
            answers = await dns.asyncresolver.resolve(input_ip, DNSRdataType.A)
        except dns.exception.DNSException:
            log.debug(_("Cannot resolve IP {} to number IP").format(input_ip))
            return input_ip

        # There should only be one answer here, though in case the server
        # does actually point to multiple IPs, we just pick the first one
        answer = answers[0]
        ip = str(answer).rstrip(".")
        return ip

    @staticmethod
    async def _get_alias_from_ip(host: str, port: int) -> typing.Optional[str]:
        """Get alias from IP.

        Args:
            host: Server's host, which exist in database.
            port: Server's port, which exist in database.

        Returns:
            Alias if found, else None.
        """
        log.debug("Address._get_alias_from_ip", host=host, port=port)
        async with models.db.session() as session:
            server = await session.execute(
                sqlalchemy.select(models.Server.alias)
                .where(models.Server.host == host)
                .where(models.Server.port == port)
            )
        row = server.first()

        log.debug("Address._get_alias_from_ip row", row=row)
        return str(row.alias) if row is not None and row.alias is not None else None


@dataclasses.dataclass
class Players:
    """Dataclass for :py:attr:`.MCServer.players` field."""

    online: int
    """Number of online players."""
    max: int
    """Maximum number of players."""

    def __str__(self) -> str:
        """Return string representation of Players object."""
        return f"{self.online}/{self.max}"


@dataclasses.dataclass
class BaseMCServer(ABC):
    """Base class for :class:`.MCServer` and :class:`.FailedMCServer`."""

    address: Address
    """:py:class:`.Address` of the server."""

    @property
    def icon(self) -> str:
        """Icon of the server.

        Returns:
            Icon of the server.
        """
        return f"https://api.mcsrvstat.us/icon/{self.address.host}:{self.address.port}"

    def __new__(cls, *args, **kwargs):
        """Prevents initialisation of this class.

        Only initialisation of children classes are allowed.
        """
        if cls is BaseMCServer:
            raise TypeError(f"Can't instantiate abstract class {cls.__name__} directly")
        return super().__new__(cls)


@dataclasses.dataclass
class MCServer(BaseMCServer):
    """Represents an MineCraft Server, doesn't depends on platform (Java or Bedrock)."""

    motd: str
    """MOTD of the server."""
    version: str
    """Name of the version, example ``1.18`` or ``1.7``."""
    players: Players
    """:py:class:`.Players` object."""
    latency: float
    """Time of response from server, in milliseconds."""

    @classmethod
    async def status(cls, host: str) -> typing.Union["MCServer", "FailedMCServer"]:
        """Get cross-platform status.

        First ping it as :py:class:`mcstatus.JavaServer`, and if it fails, ping as :py:class:`mcstatus.BedrockServer`.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``, ``hypixel.net`` or alias.

        Returns:
            Initialised :py:class:`.MCServer` object or :class:`.FailedMCServer` if ping failed.
        """
        log.debug("MCServer.status", host=host)
        success_task = await cls._handle_exceptions(
            *(
                await asyncio.wait(
                    {
                        asyncio.create_task(cls.handle_java(host), name="MCServer.handle_java"),
                        asyncio.create_task(cls.handle_bedrock(host), name="MCServer.handle_bedrock"),
                    },
                    return_when=asyncio.FIRST_COMPLETED,
                )
            )
        )

        if success_task is None:
            return await FailedMCServer.handle_failed(host)

        return success_task.result()  # type: ignore[no-any-return]

    @staticmethod
    async def _handle_exceptions(  # type: ignore[return]
        done: typing.Set[asyncio.Task], pending: typing.Set[asyncio.Task]  # type: ignore[type-arg]
    ) -> typing.Optional[asyncio.Task]:  # type: ignore[type-arg]
        """Handle exceptions in :py:meth:`.MCServer.status` method.

        This also cancels all pending tasks, if found correct one.

        Args:
            done: Direct ``done`` set from :func:`asyncio.wait` method.
            pending: All pending tasks, which will be recursively handled.

        Returns:
            Value from ``task`` parameter, or one of the success tasks from ``pending`` set.

        Raises:
            ValueError: If ``done`` set is empty.
        """
        if len(done) == 0:
            raise ValueError("No tasks was given to `done` set.")

        for i, task in enumerate(done):
            if task.exception() is not None:
                log.debug(task.get_name(), error=task.exception())
                if len(pending) == 0:
                    continue

                if i == len(done) - 1:  # firstly check all items from `done` set, and then handle pending set
                    return await MCServer._handle_exceptions(
                        *(await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED))
                    )
            else:
                for pending_task in pending:
                    pending_task.cancel()
                return task

    @classmethod
    async def handle_java(cls, host: str) -> "MCServer":
        """Handle java server and transform it to :py:class:`.MCServer` object.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``, ``hypixel.net`` or alias.

        Returns:
            Initialised :py:class:`.MCServer` object.
        """
        log.debug("MCServer.handle_java", host=host)
        address = await Address.resolve(host, java=True)
        # we access this private attribute, because it's expected behaviour to use
        # `mcstatus`' object exactly here. it must not be used anywhere else.
        status = await address._server.async_status()  # skipcq: PYL-W0212 # accessing private attribute
        return cls(
            address=address,
            motd=status.description,
            version=status.version.name,
            players=Players(
                online=status.players.online,
                max=status.players.max,
            ),
            latency=status.latency,
        )

    @classmethod
    async def handle_bedrock(cls, host: str) -> "MCServer":
        """Handle bedrock server and transform it to :py:class:`.MCServer` object.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``.

        Returns:
            Initialised :py:class:`.MCServer` object.
        """
        log.debug("MCServer.handle_bedrock", host=host)
        address = await Address.resolve(host, java=False)
        # we access this private attribute, because it's expected behaviour to use
        # `mcstatus`' object exactly here. it must not be used anywhere else.
        status = await address._server.async_status()  # skipcq: PYL-W0212 # accessing private attribute
        return cls(
            address=address,
            motd=status.motd,
            version=status.version.version,
            players=Players(
                online=status.players_online,
                max=status.players_max,
            ),
            latency=status.latency,
        )


@dataclasses.dataclass
class FailedMCServer(BaseMCServer):
    """Represents a server, when ping failed."""

    @classmethod
    async def handle_failed(cls, host: str) -> "FailedMCServer":
        """Handle failed ping and transform it to :py:class:`.MCServer` object.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``, ``hypixel.net`` or alias.

        Returns:
            Initialised :py:class:`.MCServer` object.
        """
        log.debug("MCServer.handle_failed", host=host)
        # using java=False because it is faster
        return cls(await Address.resolve(host, java=False))
