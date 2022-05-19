"""Module for the ``ping`` command."""
from re import IGNORECASE
from re import sub as re_sub

import tanjun
from hikari import Embed
from structlog.stdlib import get_logger
from tanjun.abc import SlashContext

from pinger_bot.config import gettext as _
from pinger_bot.hooks import wait_please_hook
from pinger_bot.mc_api import MCServer, StatusError

log = get_logger()

component = tanjun.Component(name="ping")


class PingCommand:
    """Cog for the ``ping`` command."""

    @staticmethod
    @wait_please_hook.add_to_command
    @component.with_slash_command
    @tanjun.with_str_slash_option("ip", _("The IP address of the server."))
    @tanjun.as_slash_command("ping", _("Ping the server and give information about it."))
    async def ping(ctx: SlashContext, ip: str) -> None:
        """Ping the server and give information about it."""
        try:
            server = await MCServer.status(ip)
        except StatusError:
            await ctx.respond(ctx.author.mention, embed=await PingCommand.get_fail_embed(ip), user_mentions=True)
            return

        embed = Embed(
            title=_("Ping Results {}").format(server.display_ip),
            description=_("Number IP: {}").format(server.num_ip),
            color=(46, 204, 113),
        )

        embed.add_field(name=_("Latency"), value=str("{:.2f}".format(server.latency)) + "мс", inline=True)
        embed.add_field(name=_("Version"), value=server.version, inline=True)
        embed.add_field(name=_("Players"), value=str(server.players), inline=True)
        embed.add_field(name=_("MOTD"), value=await PingCommand.clear_motd(server.motd))
        embed.set_thumbnail(server.icon)

        embed.set_footer(
            _("If you want to get link for editing the server MOTD, use this command: {}").format(
                f"'/motd {server.display_ip}'"
            )
        )

        await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)

    @staticmethod
    async def get_fail_embed(ip: str) -> Embed:
        """Get the embed for when the ping fails."""
        embed = Embed(title=_("Ping Results {}").format(ip), color=(231, 76, 60))
        embed.add_field(
            name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
        )
        return embed

    @staticmethod
    async def clear_motd(motd: str) -> str:
        """Clear the MOTD from the non-readable characters."""
        motd_clean = re_sub(r"[\xA7|&][0-9A-FK-OR]", "", motd, flags=IGNORECASE)
        if motd_clean == "":
            motd_clean = _("No info.")
        return motd_clean


load_slash = component.make_loader()
