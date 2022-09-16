"""Package for all commands."""
import hikari
from lightbulb.context import slash

from pinger_bot.config import gettext as _

__all__ = ["wait_please_message"]


async def wait_please_message(ctx: slash.SlashContext) -> None:
    """Factory for the ``Wait Please`` embed.

    See source code for more information.

    Args:
        ctx: The context of the command.

    Returns:
        The ``Wait Please`` embed.
    """
    embed = hikari.Embed(
        title=_("Wait please..."),
        description=_("I'm working on it, please wait. I will ping you when it's done."),
        color=(230, 126, 34),
    )
    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
