"""Module for the ``ping`` command."""
import re

import hikari.embeds as embeds
import lightbulb
import lightbulb.commands as commands
import lightbulb.context.slash as slash
import structlog.stdlib as structlog

import pinger_bot.bot as bot
import pinger_bot.config as config
import pinger_bot.ext.commands as pinger_commands
import pinger_bot.mc_api as mc_api

log = structlog.get_logger()
_ = config.gettext

plugin = lightbulb.Plugin("ping")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


async def get_fail_embed(ip: str) -> embeds.Embed:
    """Get the embed for when the ping fails.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where ping failed.
    """
    embed = embeds.Embed(title=_("Ping Results {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
    )
    return embed


async def clear_motd(motd: str) -> str:
    """Clear the :py:attr:`~pinger_bot.mc_api.MCServer.motd` from the non-readable characters.

    This removes ``&`` and ``§`` from the :py:attr:`~pinger_bot.mc_api.MCServer.motd` (plus next character).

    Args:
        motd: :py:attr:`MOTD <pinger_bot.mc_api.MCServer.motd>` of the server.

    Returns:
        Clear :py:attr:`~pinger_bot.mc_api.MCServer.motd`.
    """
    motd_clean = re.sub(r"[\xA7|&][0-9A-FK-OR]", "", motd, flags=re.IGNORECASE)
    if motd_clean == "":
        motd_clean = _("No info.")
    return motd_clean


@plugin.command
@lightbulb.option("ip", _("The IP address of the server."), type=str)
@lightbulb.command("ping", _("Ping the server and give information about it."), pass_options=True)
@lightbulb.implements(commands.SlashCommand)
async def ping(ctx: slash.SlashContext, ip: str) -> None:
    """Ping the server and give information about it.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server.
    """
    await pinger_commands.wait_please_message(ctx)
    server = await mc_api.MCServer.status(ip)
    if isinstance(server, mc_api.FailedMCServer):
        log.debug(_("Failed ping for {}").format(server.address.display_ip))
        await ctx.respond(ctx.author.mention, embed=await get_fail_embed(server.address.display_ip), user_mentions=True)
        return

    embed = embeds.Embed(
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

    log.debug(_(_("Ping successful for {}")).format(server.address.display_ip))
    await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)


def load(bot: bot.PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
