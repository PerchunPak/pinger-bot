"""Module for the ``ping`` command."""
from re import IGNORECASE
from re import sub as re_sub

from hikari import Embed
from lightbulb import Plugin, command, implements, option
from lightbulb.commands import SlashCommand
from lightbulb.context.slash import SlashContext
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot
from pinger_bot.config import gettext as _
from pinger_bot.ext.commands import wait_please_message
from pinger_bot.mc_api import MCServer, StatusError

log = get_logger()

plugin = Plugin("ping")


async def get_fail_embed(ip: str) -> Embed:
    """Get the embed for when the ping fails."""
    embed = Embed(title=_("Ping Results {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
    )
    return embed


async def clear_motd(motd: str) -> str:
    """Clear the MOTD from the non-readable characters."""
    motd_clean = re_sub(r"[\xA7|&][0-9A-FK-OR]", "", motd, flags=IGNORECASE)
    if motd_clean == "":
        motd_clean = _("No info.")
    return motd_clean


@plugin.command
@option("ip", _("The IP address of the server."), type=str)
@command("ping", _("Ping the server and give information about it."), pass_options=True)
@implements(SlashCommand)
async def ping(ctx: SlashContext, ip: str) -> None:
    """Ping the server and give information about it."""
    await wait_please_message(ctx)
    try:
        server = await MCServer.status(ip)
    except StatusError:
        await ctx.respond(ctx.author.mention, embed=await get_fail_embed(ip), user_mentions=True)
        return

    embed = Embed(
        title=_("Ping Results {}").format(server.address.display_ip),
        description=_("Number IP: {}").format(server.address.num_ip),
        color=(46, 204, 113),
    )

    embed.add_field(name=_("Latency"), value=str("{:.2f}".format(server.latency)) + "мс", inline=True)
    embed.add_field(name=_("Version"), value=server.version, inline=True)
    embed.add_field(name=_("Players"), value=str(server.players), inline=True)
    embed.add_field(name=_("MOTD"), value=await clear_motd(server.motd))
    embed.set_thumbnail(server.icon)

    embed.set_footer(
        _("If you want to get link for editing the server MOTD, use this command: {}").format(
            f"'/motd {server.address.display_ip}'"
        )
    )

    await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)


def load(bot: PingerBot) -> None:
    """Load the command."""
    bot.add_plugin(plugin)
