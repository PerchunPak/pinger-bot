"""Module for the ``add`` command."""
from hikari.embeds import Embed
from lightbulb import (
    Plugin,
    add_checks,
    command,
    implements,
    option,
    owner_only,
)
from lightbulb.commands import SlashCommand
from lightbulb.context.slash import SlashContext
from sqlalchemy.exc import IntegrityError
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot
from pinger_bot.config import gettext as _
from pinger_bot.ext.commands import wait_please_message
from pinger_bot.mc_api import FailedMCServer, MCServer
from pinger_bot.models import Server, db

log = get_logger()

plugin = Plugin("ping")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


async def get_fail_embed(ip: str) -> Embed:
    """Get the embed for when the ping fails.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where ping failed.
    """
    embed = Embed(title=_("Cannot add server {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
    )
    return embed


async def get_already_added_embed(ip: str) -> Embed:
    """Get the embed for when the server already was added.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where server was already added.
    """
    embed = Embed(title=_("Cannot add server {}").format(ip), color=(231, 76, 60))
    embed.add_field(name=_("Server was already added."), value=_("Maybe you set invalid IP address."))
    return embed


@plugin.command
@add_checks(owner_only)
@option("ip", _("The IP address of the server."), type=str)
@command("add", _("Add server to database."), pass_options=True)
@implements(SlashCommand)
async def add(ctx: SlashContext, ip: str) -> None:
    """Add a server to the database, only for owner.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server.
    """
    await wait_please_message(ctx)
    server = await MCServer.status(ip)
    if isinstance(server, FailedMCServer):
        log.debug(_("Failed ping for {}").format(server.address.display_ip))
        await ctx.respond(ctx.author.mention, embed=await get_fail_embed(server.address.display_ip), user_mentions=True)
        return

    try:
        async with db.session() as session:
            session.add(
                Server(host=server.address.host, port=server.address.port, max=server.players.max, owner=ctx.author.id)
            )
            await session.commit()
        log.debug(_("Added server {}").format(server.address.display_ip))
    except IntegrityError:  # server already added
        log.debug(_("Server {} already added").format(server.address.display_ip))
        await ctx.respond(
            ctx.author.mention, embed=await get_already_added_embed(server.address.display_ip), user_mentions=True
        )
        return

    embed = Embed(
        title=_("Added server {}").format(server.address.host),
        description=_("Name of the server in database: {}").format(
            server.address.host + ":" + str(server.address.port)
        ),
        color=(46, 204, 113),
    )

    embed.add_field(name=_("Server successfully added."), value=_("Write `/help` for more info about commands to use."))
    embed.set_thumbnail(server.icon)

    embed.set_footer(
        text=_("Now you can use `/statistic {0}`, or a `/alias {0} (your alias)` command.").format(
            server.address.display_ip
        )
    )

    await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)


def load(bot: PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
