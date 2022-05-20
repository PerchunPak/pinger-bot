"""API module with Minecraft Servers API."""
from dataclasses import dataclass

from mcstatus import BedrockServer, JavaServer
from structlog.stdlib import get_logger

from pinger_bot.config import gettext as _

log = get_logger()


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

    #: Host where server is, like ``127.0.0.1``.
    host: str
    #: Port of the server, example ``25565`` or ``19132``.
    port: int
    #: Unparsed and unmodified IP, which was passed before ``mcstatus``.
    input_ip: str
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
    #: Number IP of the server.
    num_ip: str = None  # type: ignore[assignment] # will be set in __post_init__
    #: Display IP of the server (alias, if this unset - input_ip).
    display_ip: str = None  # type: ignore[assignment] # will be set in __post_init__

    def __post_init__(self) -> None:
        """Post init method.

        Examples:
            See examples in ``MCServer.handle_java`` or ``handle_bedrock`` methods.
        """
        # it is reachable if user not defined this fields
        if self.icon is None:
            self.icon = f"https://api.mcsrvstat.us/icon/{self.host}:{str(self.port)}"  # type: ignore[unreachable]
        if self.num_ip is None:
            self.num_ip = self.host + ":" + str(self.port)  # type: ignore[unreachable]
        if self.display_ip is None:
            self.display_ip = self.input_ip  # type: ignore[unreachable]  # TODO add aliases

    @classmethod
    async def status(cls, host: str) -> "MCServer":
        """Get cross-platform status.

        First ping it as JavaServer, and if it fails, ping as BedrockServer.

        Args:
            host: Host where server is, like ``127.0.0.1:25565``.

        Returns:
            Initialised ``MCServer`` object.

        Raises:
            StatusError: When unexpected error was raised.
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
        server = await JavaServer.async_lookup(host)
        status = await server.async_status()
        return cls(
            host=server.address.host,
            port=server.address.port,
            input_ip=host,
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
        server = BedrockServer.lookup(host)
        status = await server.async_status()
        return cls(
            host=server.address.host,
            port=server.address.port,
            input_ip=host,
            motd=status.motd,
            version=status.version.version,
            players=Players(
                online=status.players_online,
                max=status.players_max,
            ),
            latency=status.latency,
        )