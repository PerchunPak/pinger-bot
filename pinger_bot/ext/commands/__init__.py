"""Package for all commands."""
from hikari import Embed, MessageFlag
from lightbulb.context.slash import SlashContext

from pinger_bot.config import gettext as _


async def wait_please_message(ctx: SlashContext) -> None:
    """Wait-please embed."""
    embed = Embed(
        title=_("Wait please..."),
        description=_("I'm working on it, please wait. I will ping you when it's done."),
        color=(230, 126, 34),
    )
    await ctx.respond(embed, flags=MessageFlag.EPHEMERAL)
