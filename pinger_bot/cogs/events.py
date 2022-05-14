"""Module for handling events."""
from nextcord.ext.commands.bot import Bot
from nextcord.ext.commands.cog import Cog
from structlog.stdlib import get_logger

from pinger_bot.config import gettext as _

log = get_logger()


class EventsCog(Cog):
    """Cog for handling events."""

    def __init__(self, bot: Bot) -> None:
        """__init__ method."""
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        """Logs when the bot is ready."""
        log.info(_("Bot running! For stop it, use CTRL C."))


def setup(bot: Bot) -> None:
    """Setup cog function."""
    bot.add_cog(EventsCog(bot))
