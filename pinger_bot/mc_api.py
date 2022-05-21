"""API module with Minecraft Servers API."""
from dataclasses import dataclass
from typing import Optional, Union

from dns.asyncresolver import resolve as dns_resolve
from dns.exception import DNSException
from dns.rdatatype import RdataType
from mcstatus import BedrockServer, JavaServer
from sqlalchemy import select
from structlog.stdlib import get_logger

from pinger_bot.config import gettext as _
from pinger_bot.models import Server, db

log = get_logger()


@dataclass
class Address:
    """Parse host and port from string, plus additional things like alias."""

    #: Host where server is, like ``127.0.0.1``.
    host: str
    #: Port of the server, example ``25565`` or ``19132``.
    port: int
    #: Unparsed and unmodified IP, which was passed before everything.
    input_ip: str
    #: Display IP of the server (alias, if this unset - input_ip).
    display_ip: str
    #: Number IP of the server. Always with port. Example ``127.0.0.1:25565``.
    num_ip: str
    #: Private attribute with JavaServer or BedrockServer instance.
    _server: Union[JavaServer, BedrockServer]

    @classmethod
    async def resolve(cls, input_ip: str, *, java: bool) -> "Address":
        """Resolve IP or domain or alias to ``Address`` object.

        Args:
            input_ip: IP or domain or alias to resolve.
            java: If True, then ``mcstatus.JavaServer`` will be used. Else - ``mcstatus.BedrockServer`` server.

        Returns:
            Resolved ``Address`` object.
        """
        ip_from_alias = await cls._get_ip_from_alias(input_ip)

        if ip_from_alias is not None:
            server = await JavaServer.async_lookup(ip_from_alias) if java else BedrockServer.lookup(ip_from_alias)
            return cls(
                host=server.address.host,
                port=server.address.port,
                input_ip=input_ip,
                display_ip=input_ip,
                num_ip=(await cls._get_number_ip(server.address.host)) + ":" + str(server.address.port),
                _server=server,
            )

        server = await JavaServer.async_lookup(input_ip) if java else BedrockServer.lookup(input_ip)
        num_ip = (await cls._get_number_ip(server.address.host)) + ":" + str(server.address.port)
        alias = await cls._get_alias_from_ip(server.address.host, server.address.port)

        return cls(
            host=server.address.host,
            port=server.address.port,
            input_ip=input_ip,
            display_ip=alias if alias is not None else input_ip,
            num_ip=num_ip,
            _server=server,
        )

    @staticmethod
    async def _get_ip_from_alias(alias: str) -> Optional[str]:
        """Get IP from alias.

        Args:
            alias: Alias to resolve.

        Returns:
            IP if alias was found, else None.
        """
        async with db.session() as session:
            server = await session.execute(select(Server.host, Server.port).where(Server.alias == alias))
        row = server.first()

        return str(row.host + ":" + str(row.port)) if row is not None else None

    @staticmethod
    async def _get_number_ip(input_ip: str) -> str:
        """Make query to DNS and get number IP.

        Args:
            input_ip: Domain to query.

        Returns:
            Number IP or input IP if resolving failed.
        """
        try:
            answers = await dns_resolve(input_ip, RdataType.A)
        except DNSException:
            log.debug(_("Cannot resolve IP {}").format(input_ip))
            return input_ip

        # There should only be one answer here, though in case the server
        # does actually point to multiple IPs, we just pick the first one
        answer = answers[0]
        ip = str(answer).rstrip(".")
        return ip

    @staticmethod
    async def _get_alias_from_ip(host: str, port: int) -> Optional[str]:
        """Get alias from IP.

        Args:
            host: Server's host, which exist in database.
            port: Server's port, which exist in database.

        Returns:
            Alias if found, else None.
        """
        async with db.session() as session:
            server = await session.execute(select(Server.alias).where(Server.host == host).where(Server.port == port))
        row = server.first()

        return str(row.alias) if row is not None else None


@dataclass
class Players:
    """Dataclass for ``MCServer.players`` field."""

    online: int
    max: int

    def __str__(self) -> str:
        """Return string representation of Players object."""
        return f"{self.online}/{self.max}"


class StatusError(Exception):
    """Raised by ``MCServer.status`` when something went wrong."""


@dataclass
class MCServer:
    """Represents an MineCraft Server, doesn't connected to platform."""

    address: Address
    #: MOTD of the server.
    motd: str
    #: Name of the version, example ``1.18`` or ``1.7``.
    version: str
    #: ``Players`` object.
    players: Players
    #: Time of response from server, in MS.
    latency: float

    #: Icon of the server.
    icon: str = None  # type: ignore[assignment] # will be set in __post_init__

    def __post_init__(self) -> None:
        """Post init method.

        Examples:
            See examples in ``MCServer.handle_java`` or ``handle_bedrock`` methods.
        """
        # it is reachable if user not defined this fields
        if self.icon is None:
            self.icon = f"https://api.mcsrvstat.us/icon/{self.address.host}:{str(self.address.port)}"  # type: ignore[unreachable]

    @classmethod
    async def status(cls, host: str) -> "MCServer":
        """Get cross-platform status.

        First ping it as JavaServer, and if it fails, ping as BedrockServer.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``, ``hypixel.net`` or alias.

        Returns:
            Initialised ``MCServer`` object.

        Raises:
            StatusError: When **any** unexpected error was raised.
        """
        log.info(_("Trying to ping {}...").format(host))
        try:
            return await cls.handle_java(host)
        except Exception as java_error:
            try:
                return await cls.handle_bedrock(host)
            except Exception as bedrock_error:
                log.debug(
                    _("Error while pinging server"),
                    host=host,
                    java_error=str(java_error),
                    bedrock_error=str(bedrock_error),
                )
                raise StatusError(_("Something went wrong, while we pinged the server."))

    @classmethod
    async def handle_java(cls, host: str) -> "MCServer":
        """Handle java server and transform it to ``MCServer`` object.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``.

        Returns:
            Initialised ``MCServer`` object.
        """
        log.debug("MCServer.handle_java", host=host)
        address = await Address.resolve(host, java=True)
        status = await address._server.async_status()
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
        """Handle bedrock server and transform it to ``MCServer`` object.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``.

        Returns:
            Initialised ``MCServer`` object.
        """
        log.debug("MCServer.handle_bedrock", host=host)
        address = await Address.resolve(host, java=False)
        status = await address._server.async_status()
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
