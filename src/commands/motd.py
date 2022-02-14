"""Модуль для команды "мотд"."""
from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands.commands_ import MetodsForCommands


class Motd(Cog):
    """Класс для команды "мотд".

    Attributes:
        bot: Атрибут для главного объекта бота.
        metods_for_commands: Инициализированный класс MetodsForCommands.
    """

    def __init__(self, bot):
        """
        Args:
            bot: Главный объект бота.
        """
        self.bot = bot
        self.metods_for_commands = MetodsForCommands(bot)

    @command(name="мотд", aliases=["motd"])
    async def motd(self, ctx, ip: str):
        """Показывает мотд и ссылку на редактирование сервера.

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
        """
        msg_wait_please = await self.metods_for_commands.wait_please(ctx, ip)
        status, info = await self.metods_for_commands.ping_server(ip)  # pylint: disable=W0612
        if status:
            embed = Embed(
                title=f"Подробное мотд сервера {info.alias if info.alias is not None else ip}",
                description="Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=Color.green(),
            )

            motd = str(status.description).replace(" ", "+")
            motd_url = motd.replace("\n", "%0A")

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.dns.host}:{str(info.dns.port)}")
            embed.add_field(name="Мотд", value=f"{status.description}")
            embed.add_field(name="Ссылка на редактирование", value="https://mctools.org/motd-creator?text=" + motd_url)
            await ctx.send(ctx.author.mention, embed=embed)
            await msg_wait_please.delete()
        else:
            embed = Embed(
                title=f"Подробное мотд сервера {info.alias if info.alias is not None else ip}",
                description="Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=Color.red(),
            )

            embed.add_field(
                name="Не удалось получить данные с сервера",
                value="Возможно вы указали неверный айпи, или сервер сейчас выключен",
            )
            await ctx.send(ctx.author.mention, embed=embed)
            await msg_wait_please.delete()


def setup(bot):
    """Добавляет класс к слушателю бота."""
    bot.add_cog(Motd(bot))
