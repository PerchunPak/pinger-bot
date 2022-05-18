"""Module for the ``ping`` command."""
import tanjun
from hikari import Embed
from structlog.stdlib import get_logger
from tanjun.abc import SlashContext

from pinger_bot.config import gettext as _
from pinger_bot.hooks import wait_please_hook

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
        embed = Embed(title=_("Ping Results"))
        await ctx.respond(embed=embed)


load_slash = component.make_loader()
