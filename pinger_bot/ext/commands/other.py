"""Module for other commands.

.. warning::
    This includes some owner-only commands, which will be shown as global.
    Waiting for the `hikari-py/hikari#1148 <https://github.com/hikari-py/hikari/pull/1148>`_ to be merged,
    and lightbulb support for those features.
"""
from json import dumps
from pathlib import Path
from subprocess import CalledProcessError, check_output
from sys import version_info

from hikari.embeds import Embed
from lightbulb import (
    Plugin,
    add_checks,
    command,
    implements,
    option,
    owner_only,
)
from lightbulb.commands import SlashCommand
from lightbulb.context.slash import SlashContext
from sqlalchemy import select, text
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot
from pinger_bot.config import gettext as _
from pinger_bot.mc_api import Address
from pinger_bot.models import Server, db

log = get_logger()

plugin = Plugin("other")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


@plugin.command
@command("about", _("Some basic information about me."))
@implements(SlashCommand)
async def about(ctx: SlashContext) -> None:
    """Some basic information about me.

    Args:
        ctx: The context of the command.
    """
    if ctx.bot.application is None:
        # This will always be ``None`` before the bot has logged in.
        return

    embed = Embed(
        title=str(ctx.bot.application),
        description=str(ctx.bot.application.description) + f"\n\n**ID**: {ctx.bot.application.id}",
        color=(153, 170, 181),
    )

    embed.add_field(name=_("Owner"), value=str(ctx.bot.application.owner), inline=True)
    embed.add_field(
        name=_("Programming language"), value=f"Python {'.'.join(map(str, version_info[:-2]))}", inline=True
    )
    embed.add_field(
        name=_("Library"),
        value="[hikari](https://github.com/hikari-py/hikari) + [lightbulb](https://github.com/tandemdude/hikari-lightbulb)",
        inline=True,
    )
    embed.add_field(
        name=_("License"),
        value="[AGPL 3.0]" "(https://github.com/PerchunPak/pinger-bot/blob/master/LICENSE)",
        inline=True,
    )
    embed.add_field(name=_("Source code"), value="https://github.com/PerchunPak/pinger-bot", inline=False)

    if ctx.bot.application.icon_url is not None:
        embed.set_thumbnail(ctx.bot.application.icon_url)

    embed.set_footer(text=_("Note: You can propose any changes to creator DM (Perchun_Pak#9236)"))
    await ctx.respond(embed=embed)


@plugin.command
@command("invite", _("Link for invite me."), ephemeral=True)
@implements(SlashCommand)
async def invite(ctx: SlashContext) -> None:
    """Link to invite the bot.

    Args:
        ctx: The context of the command.
    """
    if ctx.bot.application is None:
        # This will always be ``None`` before the bot has logged in.
        return

    msg = (
        _("This is my invite link, so you can ping servers too:")
        + f"\nhttps://discordapp.com/oauth2/authorize?client_id={ctx.bot.application.id}&permissions=2147485696&scope=bot%20applications.commands"
    )
    if not ctx.bot.application.is_bot_public:
        msg += "\n\n**" + _("WARNING: Link only working if you an owner of this bot.") + "**"

    await ctx.respond(msg)


async def get_who_owner_fail_embed(ip: str) -> Embed:
    """Get the embed for when the IP is not valid.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where command failed.
    """
    embed = Embed(title=_("Owner of the server {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't execute command."), value=_("Maybe you set invalid IP address, or server just not added.")
    )
    return embed


@plugin.command
@option("ip", _("The IP address of the server."), type=str)
@command("who_owner", _("Show owner of the server."), pass_options=True)
@implements(SlashCommand)
async def who_owner(ctx: SlashContext, ip: str) -> None:
    """Show owner of the server.

    .. note::
        If given IP without ``:``, it will be pinged as Java server. You must specify the port if it is Bedrock server.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server.
    """
    if ":" in ip:
        address = await Address.resolve(ip, java=False)
    else:
        address = await Address.resolve(ip, java=True)

    async with db.session() as session:
        server = (
            await session.scalars(select(Server).where(Server.host == address.host).where(Server.port == address.port))
        ).first()

    if server is None:
        log.debug(_("Failed get server '{}' from database").format(address.display_ip))
        await ctx.respond(
            ctx.author.mention, embed=await get_who_owner_fail_embed(address.display_ip), user_mentions=True
        )
        return

    owner = await ctx.app.rest.fetch_user(server.owner)

    embed = Embed(
        title=_("Owner of the server {}").format(address.display_ip),
        description=_("It is {}").format(owner.mention),
        color=(46, 204, 113),
    )
    embed.set_footer(_("For more information about the server, write: {}").format(f"'/statistic {address.display_ip}'"))

    await ctx.respond(embed=embed)


async def git_not_available() -> Embed:
    """Get the embed for when the git is not available.

    See source code for more information.

    Returns:
        The embed where command failed.
    """
    embed = Embed(
        title=_("Bot's version"),
        color=(231, 76, 60),
    )
    embed.add_field(name=_("GIT not available"), value=_("Unfortunately, bot can't get access to GIT."))
    return embed


@plugin.command
@command("version", _("Show bot's version."))
@implements(SlashCommand)
async def bot_version(ctx) -> None:
    """Show bot's version. I mean commit hash which was got with git.

    This also checks if ``commit.txt`` exists, which points to the commit hash in Docker.
    Please do not set this in another way.
    """
    commit_txt = Path(__file__).parent.parent.parent.parent / "commit.txt"
    if not commit_txt.exists():
        try:
            commit = check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
        except (FileNotFoundError, CalledProcessError):
            await ctx.respond(embed=await git_not_available())
            return
    else:
        with commit_txt.open("r") as commit_file:
            commit = commit_file.read().strip()

    embed = Embed(
        title=_("Bot's version"),
        color=(46, 204, 113),
    )
    embed.add_field(name=_("Commit hash"), value=commit[:7])
    embed.set_footer(text=commit)

    await ctx.respond(embed=embed)


@plugin.command
@add_checks(owner_only)
@option("sql", _("SQL statement which I pass to database."), type=str)
@option("all", _("Do I need use `.all()` on result."), type=str, choices=[_("Yes"), _("No")], default=_("Yes"))
@option("commit", _("Commit changes to database."), type=str, choices=[_("Yes"), _("No")], default=_("No"))
@command("sql", _("Execute SQL statement to database. **Owner-Only**."), pass_options=True, hidden=True)
@implements(SlashCommand)
async def sql_cmd(ctx: SlashContext, sql: str, all: str, commit: str) -> None:
    """Execute SQL statement to database. Only for owner of the bot.

    Args:
        ctx: The context of the command.
        sql: SQL statement provided by user.
        all: Do I need use ``.all()`` on SQLAlchemy result? Type :obj:`str`
            because we pass here translated ``Yes`` or ``No``.
        commit: Commit changes to database. Type :obj:`str`
            because we pass here translated ``Yes`` or ``No``.

    Returns:
        The result of the SQL statement in JSON format if ``all`` parameter is ``Yes``. Else - ``Done!`` message.
    """
    all = True if all == _("Yes") else False
    commit = True if commit == _("Yes") else False

    async with db.session() as session:
        result = await session.execute(text(sql))
        if commit:
            await session.commit()

    if not all:
        await ctx.respond(_("Done!"))
        return

    await ctx.respond("```json\n" + dumps(list(dict(row) for row in result.all()), indent=2) + "\n```")


def load(bot: PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
