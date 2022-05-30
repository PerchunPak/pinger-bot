"""Module for the ``statistic`` command."""
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional

from hikari.embeds import Embed
from lightbulb import Plugin, command, implements, option
from lightbulb.commands import SlashCommand
from lightbulb.context.slash import SlashContext
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from matplotlib.pyplot import subplots
from sqlalchemy import select
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot
from pinger_bot.config import gettext as _
from pinger_bot.ext.commands import wait_please_message
from pinger_bot.mc_api import FailedMCServer, MCServer
from pinger_bot.models import Ping, Server, db

log = get_logger()

plugin = Plugin("statistic")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


async def get_not_in_db_embed(ip: str) -> Embed:
    """Get the embed when a server not in database.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where server not in database.
    """
    embed = Embed(title=_("{} statistic").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't find the server in database."),
        value=_("Maybe you set invalid IP address, or server just offline."),
    )
    return embed


async def get_yesterday_ping(pings: List[Ping]) -> Optional[Ping]:
    """Get the ping from yesterday.

    Yesterday - it is period between 23-25 hours.

    Args:
        pings: List of server's :class:`pings <pinger_bot.models.Ping>`.

    Returns:
        :class:`~pinger_bot.models.Ping` or :obj:`None` if no yesterday ping.
    """
    yesterday_25h = datetime.now() - timedelta(hours=25)
    yesterday_23h = datetime.now() - timedelta(hours=23)
    yesterday_ping: Optional[Ping] = None
    for ping in pings:  # search pings in range 23-25 hours ago
        if yesterday_23h > ping.time > yesterday_25h:
            yesterday_ping = ping
    return yesterday_ping


async def create_plot(pings: List[Ping], ip: str) -> Figure:
    """Create plot for the server.

    Args:
        pings: List of server's :class:`pings <pinger_bot.models.Ping>`.
        ip: IP of the server, which referenced in text. Better set it to :attr:`~pinger_bot.mc_api.Address.display_ip`.

    Returns:
        :class:`~matplotlib.figure.Figure` object.
    """
    online: List[int] = []
    time: List[datetime] = []
    for ping in pings:
        online.append(ping.players)
        time.append(ping.time)

    figure, axes = subplots()
    axes.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    axes.plot(time, online)

    axes.set_xlabel(_("Time"))
    axes.set_ylabel(_("Players online"))
    axes.set_title(_("{} statistic").format(ip))

    return figure


async def transform_figure_to_bytes(figure: Figure) -> BytesIO:
    """Transform :class:`~matplotlib.figure.Figure` to :class:`~io.BytesIO`.

    Args:
        figure: :class:`~matplotlib.figure.Figure` of the plot.

    Returns:
        :class:`~io.BytesIO` object.
    """
    buffer = BytesIO()
    figure.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer


@plugin.command
@option("ip", _("The IP address of the server."), type=str)
@command("statistic", _("Some statistic about the server."), pass_options=True)
@implements(SlashCommand)
async def statistic(ctx: SlashContext, ip: str) -> None:
    """Some statistic about the server. It's working, even if server is offline.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server.
    """
    await wait_please_message(ctx)
    server = await MCServer.status(ip)

    async with db.session() as session:
        db_server: Optional[Server] = (
            await session.scalars(
                select(Server).where(Server.host == server.address.host).where(Server.port == server.address.port)
            )
        ).first()

        if db_server is None:
            log.debug(_("Server {} not found in database").format(server.address.display_ip))
            await ctx.respond(
                ctx.author.mention, embed=await get_not_in_db_embed(server.address.display_ip), user_mentions=True
            )
            return

        pings = (
            await session.scalars(select(Ping).where(Ping.host == db_server.host).where(Ping.port == db_server.port))
        ).all()
    yesterday_ping = await get_yesterday_ping(pings)

    embed = Embed(
        title=_("{} statistic").format(server.address.display_ip),
        description=_("Number IP: {}").format(server.address.num_ip)
        + "\n\n**"
        + (_("Online") if not isinstance(server, FailedMCServer) else _("Offline"))
        + "**",
        color=(46, 204, 113),
    )

    players = server.players if not isinstance(server, FailedMCServer) else _("No info.")
    yesterday_online = str(yesterday_ping.players) if yesterday_ping is not None else _("No info.")

    embed.add_field(name=_("Current online"), value=str(players), inline=True)
    embed.add_field(name=_("Yesterday online, in same time"), value=yesterday_online, inline=True)
    embed.add_field(name=_("Max online of all time"), value=str(db_server.max), inline=True)
    embed.set_thumbnail(server.icon)

    embed.set_footer(
        _("For more information about the server, write: {}").format(f"'/ping {server.address.display_ip}'")
    )

    if len(pings) <= 20:
        await ctx.respond(ctx.author.mention + ", " + _("not enough info for a plot."), embed=embed, user_mentions=True)
        return

    figure = await create_plot(pings, server.address.display_ip)
    embed.set_image(await transform_figure_to_bytes(figure))
    await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)


def load(bot: PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
