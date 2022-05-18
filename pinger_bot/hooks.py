"""Module for handling events."""
from hikari import StartedEvent
from structlog.stdlib import get_logger
from tanjun import SlashHooks
from tanjun.abc import SlashContext

from pinger_bot.config import gettext as _

log = get_logger()

hooks = SlashHooks()


class Hooks:
    """Class for handling events."""

    @staticmethod
    @hooks.with_pre_execution
    async def pre_execution(ctx: SlashContext) -> None:
        """Pre-execution hook. Just logs the call of command.

        Args:
            ctx: Context of the command.

        """
        if ctx.command is None:
            return

        options = {}
        for key in ctx.options:
            options[key] = ctx.options[key].value

        log.debug(_("Command '{}'").format(ctx.command.name), user=str(ctx.author), **options)

    @staticmethod
    async def on_started(event: StartedEvent) -> None:
        """On-started hook. Just logs that the bot started."""
        log.info(_("Bot running! For stop it, use CTRL C."))
