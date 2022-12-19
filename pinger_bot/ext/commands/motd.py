"""Module for the ``motd`` command."""
import urllib.parse

import lightbulb
from hikari import embeds
from lightbulb import commands
from lightbulb.context import slash
from structlog import stdlib as structlog

from pinger_bot import bot, mc_api
from pinger_bot.config import gettext as _
from pinger_bot.ext import commands as pinger_commands

log = structlog.get_logger()

plugin = lightbulb.Plugin("motd")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


async def get_fail_embed(ip: str) -> embeds.Embed:
    """Get the embed for when the ping fails.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where ping failed.
    """
    embed = embeds.Embed(title=_("Detailed MOTD of the {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
    )
    return embed


@plugin.command
@lightbulb.option("ip", _("The IP address of the server."), type=str)
@lightbulb.command("motd", _("Get link for editing the server MOTD."), pass_options=True)
@lightbulb.implements(commands.SlashCommand)
async def motd(ctx: slash.SlashContext, ip: str) -> None:
    """Ping the server and give information about it.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server to ping.
    """
    await pinger_commands.wait_please_message(ctx)
    server = await mc_api.MCServer.status(ip)
    if isinstance(server, mc_api.FailedMCServer):
        log.debug(_("Failed ping for {}").format(server.address.display_ip))
        await ctx.respond(ctx.author.mention, embed=await get_fail_embed(server.address.display_ip), user_mentions=True)
        return

    embed = embeds.Embed(
        title=_("Detailed MOTD of the {}").format(server.address.display_ip),
        description=_("This command give ability to edit the MOTD of the server."),
        color=(46, 204, 113),
    )

    embed.add_field(name=_("MOTD"), value=server.motd)
    embed.add_field(
        name=_("Link for editing"),
        value="https://mctools.org/motd-creator?text=" + urllib.parse.quote_plus(server.motd),
    )
    embed.set_thumbnail(server.icon)

    log.debug(_("Ping successful for {}").format(server.address.display_ip))
    await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)


def load(bot_instance: bot.PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot_instance.add_plugin(plugin)
