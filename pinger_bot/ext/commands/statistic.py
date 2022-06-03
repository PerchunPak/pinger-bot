"""Module for the ``statistic`` command."""
import datetime
import io
import typing

import hikari.embeds as embeds
import lightbulb
import lightbulb.commands as commands
import lightbulb.context.slash as slash
import matplotlib.dates as dates
import matplotlib.figure as figure
import matplotlib.pyplot as pyplot
import sqlalchemy
import structlog.stdlib as structlog

import pinger_bot.bot as bot
import pinger_bot.config as config
import pinger_bot.ext.commands as pinger_commands
import pinger_bot.mc_api as mc_api
import pinger_bot.models as models

log = structlog.get_logger()
_ = config.gettext

plugin = lightbulb.Plugin("statistic")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


async def get_not_in_db_embed(ip: str) -> embeds.Embed:
    """Get the embed when a server not in database.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where server not in database.
    """
    embed = embeds.Embed(title=_("{} statistic").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't find the server in database."),
        value=_("Maybe you set invalid IP address, or server just offline."),
    )
    return embed


async def get_yesterday_ping(pings: typing.List[models.Ping]) -> typing.Optional[models.Ping]:
    """Get the ping from yesterday.

    Yesterday - it is period between 23-25 hours.

    Args:
        pings: List of server's :class:`pings <pinger_bot.models.Ping>`.

    Returns:
        :class:`~pinger_bot.models.Ping` or :obj:`None` if no yesterday ping.
    """
    yesterday_25h = datetime.datetime.now() - datetime.timedelta(hours=25)
    yesterday_23h = datetime.datetime.now() - datetime.timedelta(hours=23)
    yesterday_ping: typing.Optional[models.Ping] = None
    for ping in pings:  # search pings in range 23-25 hours ago
        if yesterday_23h > ping.time > yesterday_25h:
            yesterday_ping = ping
    return yesterday_ping


async def create_plot(pings: typing.List[models.Ping], ip: str) -> figure.Figure:
    """Create plot for the server.

    Args:
        pings: List of server's :class:`pings <pinger_bot.models.Ping>`.
        ip: IP of the server, which referenced in text. Better set it to :attr:`~pinger_bot.mc_api.Address.display_ip`.

    Returns:
        :class:`~matplotlib.figure.Figure` object.
    """
    online: typing.List[int] = []
    time: typing.List[datetime.datetime] = []
    for ping in pings:
        online.append(ping.players)
        time.append(ping.time)

    figure, axes = pyplot.subplots()
    axes.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    axes.plot(time, online)

    axes.set_xlabel(_("Time"))
    axes.set_ylabel(_("Players online"))
    axes.set_title(_("{} statistic").format(ip))

    return figure


async def transform_figure_to_bytes(figure: figure.Figure) -> io.BytesIO:
    """Transform :class:`~matplotlib.figure.Figure` to :class:`~io.BytesIO`.

    Args:
        figure: :class:`~matplotlib.figure.Figure` of the plot.

    Returns:
        :class:`~io.BytesIO` object.
    """
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer


@plugin.command
@lightbulb.option("ip", _("The IP address of the server."), type=str)
@lightbulb.command("statistic", _("Some statistic about the server."), pass_options=True)
@lightbulb.implements(commands.SlashCommand)
async def statistic(ctx: slash.SlashContext, ip: str) -> None:
    """Some statistic about the server. It's working, even if server is offline.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server.
    """
    await pinger_commands.wait_please_message(ctx)
    server = await mc_api.MCServer.status(ip)

    async with models.db.session() as session:
        db_server: typing.Optional[models.Server] = (
            await session.scalars(
                sqlalchemy.select(models.Server)
                .where(models.Server.host == server.address.host)
                .where(models.Server.port == server.address.port)
            )
        ).first()

        if db_server is None:
            log.debug(_("Server {} not found in database").format(server.address.display_ip))
            await ctx.respond(
                ctx.author.mention, embed=await get_not_in_db_embed(server.address.display_ip), user_mentions=True
            )
            return

        pings = (
            await session.scalars(
                sqlalchemy.select(models.Ping)
                .where(models.Ping.host == db_server.host)
                .where(models.Ping.port == db_server.port)
            )
        ).all()
    yesterday_ping = await get_yesterday_ping(pings)

    embed = embeds.Embed(
        title=_("{} statistic").format(server.address.display_ip),
        description=_("Number IP: {}").format(server.address.num_ip)
        + "\n\n**"
        + (_("Online") if not isinstance(server, mc_api.FailedMCServer) else _("Offline"))
        + "**",
        color=(46, 204, 113),
    )

    players = server.players if not isinstance(server, mc_api.FailedMCServer) else _("No info.")
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


def load(bot: bot.PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
