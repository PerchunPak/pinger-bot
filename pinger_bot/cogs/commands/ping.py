"""Module for the ``ping`` command."""
from nextcord import Embed, Interaction, slash_command
from nextcord.ext.commands.bot import Bot
from nextcord.ext.commands.cog import Cog
from structlog.stdlib import get_logger

log = get_logger()


class PingCommandCog(Cog):
    """Cog for the ``ping`` command."""

    def __init__(self, bot: Bot) -> None:
        """__init__ method."""
        self.bot = bot

    @slash_command()
    async def ping(self, interaction: Interaction) -> None:
        """Just a ping command."""
        log.debug("ping command", user=interaction.user, message=interaction.message, channel=interaction.channel)
        embed = Embed(title="Результат пинга")
        await interaction.response.send_message(embed=embed)


def setup(bot):
    """Default setup function."""
    bot.add_cog(PingCommandCog(bot))
