"""Module for handling events."""
from hikari import StartedEvent, StoppingEvent
from lightbulb import Plugin
from lightbulb.events import SlashCommandInvocationEvent
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot
from pinger_bot.config import gettext as _

log = get_logger()

plugin = Plugin(name="events")


class Events:
    """Class for handling events."""

    @staticmethod
    @plugin.listener(SlashCommandInvocationEvent)
    async def pre_execution(event: SlashCommandInvocationEvent) -> None:
        """Pre-execution hook. Just logs the call of command.

        Args:
            event: Event that triggered listener.

        """
        if event.context.command is None:
            return

        options = {}
        for key in event.context.raw_options:
            options[key] = event.context.raw_options[key]

        log.debug(_("Command '{}'").format(event.context.command.name), user=str(event.context.author), **options)

    @staticmethod
    @plugin.listener(StartedEvent)
    async def on_started(event: StartedEvent) -> None:
        """On-started hook. Just logs that the bot started."""
        log.info(_("Bot running! For stop it, use CTRL C."))

    @staticmethod
    @plugin.listener(StoppingEvent)
    async def on_stopping(event: StoppingEvent) -> None:
        """On-started hook. Just logs that the bot started."""
        log.info(_("Bot stopping. Bye!"))


def load(bot: PingerBot) -> None:
    """Load the command."""
    bot.add_plugin(plugin)
