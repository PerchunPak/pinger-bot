"""Module for handling events."""
import lightbulb
from hikari.events import lifetime_events
from lightbulb import events
from structlog import stdlib as structlog

from pinger_bot import bot
from pinger_bot.config import gettext as _
from pinger_bot.ext import scheduling

log = structlog.get_logger()

plugin = lightbulb.Plugin(name="events")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


class Events:
    """Class for handling events."""

    @staticmethod
    @plugin.listener(events.SlashCommandInvocationEvent)
    async def pre_execution(event: events.SlashCommandInvocationEvent) -> None:
        """Pre-execution hook. Just logs the call of command.

        Args:
            event: Event that triggered listener.
        """
        if event.context.command is None:
            return

        options = {}
        for key in event.context.raw_options:
            options[key] = event.context.raw_options[key]

        log.info(_("Command '{}'").format(event.context.command.name), user=str(event.context.author), **options)

    @staticmethod
    @plugin.listener(lifetime_events.StartedEvent)
    async def on_started(event: lifetime_events.StartedEvent) -> None:
        """On-started hook. Just logs that the bot started and run scheduler."""
        log.info(_("Bot running! For stop it, use CTRL C."))
        scheduling.scheduler.start()

    @staticmethod
    @plugin.listener(lifetime_events.StoppingEvent)
    async def on_stopping(event: lifetime_events.StoppingEvent) -> None:
        """On-started hook. Just logs that the bot stopping and stop scheduler."""
        log.info(_("Bot stopping. Bye!"))
        scheduling.scheduler.shutdown()


def load(bot_obj: bot.PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot_obj.add_plugin(plugin)
