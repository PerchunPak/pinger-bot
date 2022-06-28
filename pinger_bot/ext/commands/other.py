"""Module for other commands.

.. warning::
    This includes some owner-only commands, which will be shown as global.
    Waiting for the `lightbulb support <https://github.com/tandemdude/hikari-lightbulb/pull/259>`_
    for supporting hiding commands from global list (Application Permissions v2).
"""
import json
import pathlib
import subprocess
import sys

import aiohttp
import asyncache
import cachetools
import hikari.embeds as embeds
import lightbulb
import lightbulb.commands as commands
import lightbulb.context.slash as slash
import sqlalchemy
import sqlalchemy.exc
import structlog.stdlib as structlog

import pinger_bot.bot as bot
import pinger_bot.config as config
import pinger_bot.mc_api as mc_api
import pinger_bot.models as models

log = structlog.get_logger()
_ = config.gettext

plugin = lightbulb.Plugin("other")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


@plugin.command
@lightbulb.command("about", _("Some basic information about me."))
@lightbulb.implements(commands.SlashCommand)
async def about(ctx: slash.SlashContext) -> None:
    """Some basic information about me.

    Args:
        ctx: The context of the command.
    """
    if ctx.bot.application is None:
        # This will always be ``None`` before the bot has logged in.
        return

    embed = embeds.Embed(
        title=str(ctx.bot.application),
        description=str(ctx.bot.application.description) + f"\n\n**ID**: {ctx.bot.application.id}",
        color=(153, 170, 181),
    )

    embed.add_field(name=_("Owner"), value=str(ctx.bot.application.owner), inline=True)
    embed.add_field(
        name=_("Programming language"), value=f"Python {'.'.join(map(str, sys.version_info[:-2]))}", inline=True
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
@lightbulb.command("invite", _("Link for invite me."), ephemeral=True)
@lightbulb.implements(commands.SlashCommand)
async def invite(ctx: slash.SlashContext) -> None:
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


async def get_who_owner_fail_embed(ip: str) -> embeds.Embed:
    """Get the embed for when the IP is not valid.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where command failed.
    """
    embed = embeds.Embed(title=_("Owner of the server {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't execute command."), value=_("Maybe you set invalid IP address, or server just not added.")
    )
    return embed


@plugin.command
@lightbulb.option("ip", _("The IP address of the server."), type=str)
@lightbulb.command("who_owner", _("Show owner of the server."), pass_options=True)
@lightbulb.implements(commands.SlashCommand)
async def who_owner(ctx: slash.SlashContext, ip: str) -> None:
    """Show owner of the server.

    .. note::
        If given IP without ``:``, it will be pinged as Java server. You must specify the port if it is Bedrock server.

    Args:
        ctx: The context of the command.
        ip: The IP address of the server.
    """
    if ":" in ip:
        address = await mc_api.Address.resolve(ip, java=False)
    else:
        address = await mc_api.Address.resolve(ip, java=True)

    async with models.db.session() as session:
        server = (
            await session.scalars(
                sqlalchemy.select(models.Server)
                .where(models.Server.host == address.host)
                .where(models.Server.port == address.port)
            )
        ).first()

    if server is None:
        log.debug(_("Failed get server '{}' from database").format(address.display_ip))
        await ctx.respond(
            ctx.author.mention, embed=await get_who_owner_fail_embed(address.display_ip), user_mentions=True
        )
        return

    owner = await ctx.app.rest.fetch_user(server.owner)

    embed = embeds.Embed(
        title=_("Owner of the server {}").format(address.display_ip),
        description=_("It is {}").format(owner.mention),
        color=(46, 204, 113),
    )
    embed.set_footer(_("For more information about the server, write: {}").format(f"'/statistic {address.display_ip}'"))

    await ctx.respond(embed=embed)


async def git_not_available() -> embeds.Embed:
    """Get the embed for when the git is not available.

    See source code for more information.

    Returns:
        The embed where command failed.
    """
    embed = embeds.Embed(
        title=_("Bot's version"),
        color=(231, 76, 60),
    )
    embed.add_field(name=_("GIT not available"), value=_("Unfortunately, bot can't get access to GIT."))
    return embed


@asyncache.cached(cachetools.TTLCache(1024, 3600))
async def get_bot_latest_version() -> str:
    """Get latest commit on ``master`` branch and cache it.

    Cache resets every hour, or every 1024 usages.

    Returns:
        Short SHA256 of last commit or translated ``Not available``.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.github.com/repos/PerchunPak/pinger-bot/commits/master",
            headers={"Accept": "application/vnd.github.VERSION.sha"},
        ) as response:
            return (await response.text())[:7] if response.ok else _("Not available")


@plugin.command
@lightbulb.command("version", _("Show bot's version."))
@lightbulb.implements(commands.SlashCommand)
async def bot_version(ctx) -> None:
    """Show bot's version. I mean commit hash which was got with git.

    This also checks if ``commit.txt`` exists, which points to the commit hash in Docker.
    Please do not set this in another way.
    """
    commit_txt = pathlib.Path(__file__).parent.parent.parent.parent / "commit.txt"
    if not commit_txt.exists():
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            await ctx.respond(embed=await git_not_available())
            return
    else:
        with commit_txt.open("r") as commit_file:
            commit = commit_file.read().strip()

    last_commit = await get_bot_latest_version()

    embed = embeds.Embed(
        title=_("Bot's version"),
        color=(46, 204, 113),
    )
    embed.add_field(name=_("Commit hash"), value=commit[:7])
    embed.set_footer(text=_("Last version: ") + last_commit)

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("sql", _("SQL statement which I pass to database."), type=str)
@lightbulb.option("commit", _("Commit changes to database."), type=str, choices=[_("Yes"), _("No")], default=_("No"))
@lightbulb.command("sql", _("Execute SQL statement to database. **Owner-Only**."), pass_options=True, hidden=True)
@lightbulb.implements(commands.SlashCommand)
async def sql_cmd(ctx: slash.SlashContext, sql: str, commit: str) -> None:
    """Execute SQL statement to database. Only for owner of the bot.

    Args:
        ctx: The context of the command.
        sql: SQL statement provided by user.
        commit: Commit changes to database. Type :obj:`str`
            because we pass here translated ``Yes`` or ``No``.

    Returns:
        The result of the SQL statement in JSON format if ``all`` parameter is ``Yes``. Else - ``Done!`` message.
    """
    commit = commit == _("Yes")

    async with models.db.session() as session:
        result = await session.execute(sqlalchemy.text(sql))
        if commit:
            await session.commit()

    try:
        message = "```json\n" + json.dumps(list(dict(row) for row in result.all()), indent=2) + "\n```"
    except sqlalchemy.exc.ResourceClosedError:
        message = _("Done!")

    await ctx.respond(message)


def load(bot: bot.PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
