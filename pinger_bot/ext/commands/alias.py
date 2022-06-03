"""Module for the ``alias`` command."""
import hikari.embeds as embeds
import lightbulb
import lightbulb.commands as commands
import lightbulb.context.slash as slash
import sqlalchemy
import structlog.stdlib as structlog

import pinger_bot.bot as bot
import pinger_bot.config as config
import pinger_bot.ext.commands as pinger_commands
import pinger_bot.mc_api as mc_api
import pinger_bot.models as models

log = structlog.get_logger()
_ = config.gettext

plugin = lightbulb.Plugin("alias")
""":class:`lightbulb.Plugin <lightbulb.plugins.Plugin>` object."""


async def get_fail_embed(ip: str) -> embeds.Embed:
    """Get the embed for when the something fails.

    See source code for more information.

    Args:
        ip: The IP address of the server to reference in text.

    Returns:
        The embed where ping failed.
    """
    embed = embeds.Embed(title=_("Ping Results {}").format(ip), color=(231, 76, 60))
    embed.add_field(
        name=_("Can't ping the server."), value=_("Maybe you set invalid IP address, or server just offline.")
    )
    return embed


async def get_not_owner_embed(server: mc_api.MCServer) -> embeds.Embed:
    """Get the embed when user not owner of the server.

    Args:
        server: :class:`~pinger_bot.mc_api.MCServer` object.

    Returns:
        The embed where user not owner of the server.
    """
    embed = embeds.Embed(
        title=_("You are not an owner of the server"),
        description=_("Only server's owner can set/change alias."),
        color=(231, 76, 60),
    )
    embed.add_field(
        name=_("Can't set alias."),
        value=_("You are not owner of the server {}.").format(server.address.display_ip),
    )
    embed.set_thumbnail(server.icon)

    embed.set_footer(
        _("For more information about the server, write: {}").format(f"'/statistic {server.address.display_ip}'")
    )
    return embed


async def get_alias_exists_embed(server: mc_api.MCServer, input_alias: str) -> embeds.Embed:
    """Get the embed when alias already exists.

    Args:
        server: :class:`~pinger_bot.mc_api.MCServer` object.
        input_alias: Alias inputted by user.

    Returns:
        The embed where alias already exists.
    """
    embed = embeds.Embed(
        title=_("Alias {} already exists").format(input_alias),
        description=_("You can add only not existing alias."),
        color=(231, 76, 60),
    )
    embed.add_field(name=_("Error"), value=_("Alias already exists.").format(input_alias))
    embed.set_thumbnail(server.icon)

    embed.set_footer(
        _("For more information about the server, write: {}").format(f"'/statistic {server.address.display_ip}'")
    )

    return embed


@plugin.command
@lightbulb.option("ip", _("The IP address or alias of the server."), type=str)
@lightbulb.option("alias", _("New alias of the server."), type=str)
@lightbulb.command("alias", _("Set alias of the server."), pass_options=True)
@lightbulb.implements(commands.SlashCommand)
async def alias_cmd(ctx: slash.SlashContext, ip: str, alias: str) -> None:
    """Ping the server and give information about it.

    Args:
        ctx: The context of the command.
        ip: The IP address or alias of the server.
        alias: New alias of the server.
    """
    await pinger_commands.wait_please_message(ctx)
    server = await mc_api.MCServer.status(ip)

    if isinstance(server, mc_api.FailedMCServer):
        log.debug(_("Failed ping for {}").format(server.address.display_ip))
        row = None
    else:
        async with models.db.session() as session:
            db_server = await session.execute(
                sqlalchemy.select(models.Server.id, models.Server.owner)
                .where(models.Server.host == server.address.host)
                .where(models.Server.port == server.address.port)
            )
        row = db_server.first()
        log.debug(_("Server {} in DB {}").format(server.address.display_ip, row))

    if row is None or isinstance(
        server, mc_api.FailedMCServer
    ):  # isinstance only for type checker, it is always will be True
        log.debug(
            _("Failed add alias for {}.").format(server.address.display_ip) + _("Server offline or not in database.")
        )
        await ctx.respond(ctx.author.mention, embed=await get_fail_embed(server.address.display_ip), user_mentions=True)
        return

    if ctx.author.id != row.owner:
        log.debug(_("Failed add alias for {}.").format(server.address.display_ip) + _("User not owner."))
        await ctx.respond(ctx.author.mention, embed=await get_not_owner_embed(server), user_mentions=True)
        return

    try:
        async with models.db.session() as session:
            await session.execute(
                sqlalchemy.update(models.Server).where(models.Server.id == row.id).values(alias=alias)
            )
            await session.commit()
        log.debug("Server {}'s alias changed to {}".format(server.address.display_ip, alias))
    except sqlalchemy.exc.IntegrityError:
        log.debug(_("Failed add alias for {}.").format(server.address.display_ip) + _("Alias already exists."))
        await ctx.respond(ctx.author.mention, embed=await get_alias_exists_embed(server, alias), user_mentions=True)
        return

    embed = embeds.Embed(
        title=_("Added alias {} to server {}").format(alias, server.address.display_ip),
        description=_("Now you can use {} instead of {}").format(alias, server.address.display_ip),
        color=(46, 204, 113),
    )

    embed.add_field(
        name=_("Data successfully updated"), value=_("See '/' preview for list of my commands"), inline=True
    )
    embed.set_thumbnail(server.icon)

    embed.set_footer(_("For more information about the server, write: {}").format(f"'/statistic {alias}'"))

    await ctx.respond(ctx.author.mention, embed=embed, user_mentions=True)


def load(bot: bot.PingerBot) -> None:
    """Load the :py:data:`plugin`."""
    bot.add_plugin(plugin)
