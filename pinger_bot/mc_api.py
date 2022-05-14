"""API module with Minecraft Servers API."""
from dataclasses import dataclass

from mcstatus import BedrockServer, JavaServer
from structlog.stdlib import get_logger

log = get_logger()


@dataclass
class Players:
    """Dataclass for ``MCServer.players`` field."""

    online: int
    max: int


class StatusError(Exception):
    """Raised by ``MCServer.status`` when something went wrong."""


class MCServer:
    """Represents an MineCraft Server, doesn't connected to platform."""

    def __init__(
        self,
        host: str,
        port: int,
        motd: str,
        version: str,
        players: Players,
        latency: float,
    ) -> None:
        """__init__ method.

        Args:
            host: Host where server is, like ``127.0.0.1``.
            port: Port of the server, example ``25565`` or ``19132``.
            motd: MOTD of the server.
            version: Name of the version, example ``1.18`` or ``1.7``.
            players: ``Players`` object.
            latency: Time of response from server, in MS.

        Examples:
            See examples in ``MCServer.handle_java`` or ``handle_bedrock`` methods.
        """
        self.host = host
        self.port = port
        self.num_ip = self.host + ":" + str(self.port)
        self.motd = motd
        self.version = version
        self.players = players
        self.image = f"https://api.mcsrvstat.us/icon/{self.host}:{str(self.port)}"
        self.latency = latency

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
        log.info("Trying to ping {}...".format(host))
        try:
            server = await JavaServer.async_lookup(host)
            return await cls.handle_java(server)
        except Exception:
            try:
                server = BedrockServer.lookup(host)
                return await cls.handle_bedrock(server)
            except Exception as exception:
                log.debug("Error while pinging server", host=host, exception=exception)
                raise StatusError("Something went wrong, while we pinged the server.")

    @classmethod
    async def handle_java(cls, server: JavaServer) -> "MCServer":
        """Handle java server and transform it to ``MCServer`` object.

        Args:
            server: ``mcstatus.JavaServer`` object.

        Returns:
            Initialised ``MCServer`` object.
        """
        log.debug("MCServer.handle_java", host=server.address.host, port=server.address.port)
        status = await server.async_status()
        return cls(
            host=server.address.host,
            port=server.address.port,
            motd=status.description,
            version=status.version.name,
            players=Players(
                online=status.players.online,
                max=status.players.max,
            ),
            latency=status.latency,
        )

    @classmethod
    async def handle_bedrock(cls, server: BedrockServer) -> "MCServer":
        """Handle bedrock server and transform it to ``MCServer`` object.

        Args:
            server: ``mcstatus.BedrockServer`` object.

        Returns:
            Initialised ``MCServer`` object.
        """
        log.debug("MCServer.handle_bedrock", host=server.address.host, port=server.address.port)
        status = await server.async_status()
        return cls(
            host=server.address.host,
            port=server.address.port,
            motd=status.motd,
            version=status.version.version,
            players=Players(
                online=status.players_online,
                max=status.players_max,
            ),
            latency=status.latency,
        )
