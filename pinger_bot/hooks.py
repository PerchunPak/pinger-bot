"""Module for handling events."""
from hikari import Embed, StartedEvent
from structlog.stdlib import get_logger
from tanjun import SlashHooks
from tanjun.abc import SlashContext

from pinger_bot.config import gettext as _

log = get_logger()

hooks = SlashHooks()
wait_please_hook = SlashHooks()


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
    @wait_please_hook.with_pre_execution
    async def wait_please_message(ctx: SlashContext) -> None:
        """Wait-please embed."""
        embed = Embed(
            title=_("Wait please..."),
            description=_("I'm working on it, please wait. I will ping you when it's done."),
            color=(230, 126, 34),
        )
        await ctx.create_initial_response(embed=embed, ephemeral=True)

    @staticmethod
    async def on_started(event: StartedEvent) -> None:
        """On-started hook. Just logs that the bot started."""
        log.info(_("Bot running! For stop it, use CTRL C."))
