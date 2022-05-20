"""Module for the ``motd`` command."""
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

plugin = Plugin("motd")


class MotdCommand:
    """Class for the ``motd`` command."""

    @staticmethod
    @plugin.command
    @option("ip", _("The IP address of the server."), type=str)
    @command("motd", _("Get link for editing the server MOTD."), pass_options=True)
    @implements(SlashCommand)
    async def motd(ctx: SlashContext, ip: str) -> None:
        """Ping the server and give information about it."""
        await wait_please_message(ctx)
        try:
            server = await MCServer.status(ip)
        except StatusError:
            await ctx.respond(ctx.author.mention, embed=await MotdCommand.get_fail_embed(ip), user_mentions=True)
            return

        embed = Embed(
            title=_("Detailed MOTD of the {}").format(server.display_ip),
            description=_("This command give ability to edit the MOTD of the server."),
            color=(46, 204, 113),
        )

        motd_url = server.motd.replace(" ", "+").replace("\n", "%0A")

        embed.add_field(name=_("MOTD"), value=server.motd)
        embed.add_field(name=_("Link for editing"), value="https://mctools.org/motd-creator?text=" + motd_url)
        embed.set_thumbnail(server.icon)

        await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)

    @staticmethod
    async def get_fail_embed(ip: str) -> Embed:
        """Get the embed for when the ping fails."""
        embed = Embed(title=_("Detailed MOTD of the {}").format(ip), color=(231, 76, 60))
        embed.add_field(
            name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
        )
        return embed


def load(bot: PingerBot) -> None:
    """Load the command."""
    bot.add_plugin(plugin)
