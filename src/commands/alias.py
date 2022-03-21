"""Модуль для команды "алиас"."""
from asyncpg.exceptions import UniqueViolationError
from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands.commands_ import MetodsForCommands


class Alias(Cog):
    """Класс для команды "алиас".

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

    @command(name="алиас", aliases=["alias"])
    async def alias(self, ctx, alias: str, ip: str):
        """Добавление алиаса к серверу.

        Args:
            ctx: Объект сообщения.
            alias: Новый алиас сервера.
            ip: Айпи сервера.

        Returns:
            Объект отправленного сообщения, чтобы остановить команду.
        """
        msg_wait_please = await self.metods_for_commands.wait_please(ctx, ip)
        status, info = await self.metods_for_commands.ping_server(ip)  # pylint: disable=W0612
        if info.valid and status:
            database_server = await self.bot.db.get_server(info.dns.host, info.dns.port)
        else:
            database_server = {}
        if len(database_server) != 0:
            name = info.alias if info.alias is not None else ip
            if ctx.author.id != database_server["owner"]:
                embed = Embed(
                    title=f"Вы не владелец сервера {name}",
                    description=f"Только владелец может изменить/добавить алиас сервера {name}",
                    color=Color.red(),
                )

                embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.dns.host}:{str(info.dns.port)}")
                embed.add_field(name="Ошибка", value="Вы не владелец")
                embed.set_footer(text=f'Для большей информации о сервере напишите "стата {name}"')

                await ctx.send(ctx.author.mention, embed=embed)
                await msg_wait_please.delete()
                return

            try:
                await self.bot.db.add_alias(alias, info.dns.host, info.dns.port)
            except UniqueViolationError:
                embed = Embed(
                    title=f"Алиас {alias} уже существует",
                    description="Можно добавить только не существующий алиас",
                    color=Color.red(),
                )

                embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.dns.host}:{str(info.dns.port)}")
                embed.add_field(name="Ошибка", value="Алиас уже существует")
                embed.set_footer(text=f'Для большей информации о сервере напишите "пинг {name}"')

                await ctx.send(ctx.author.mention, embed=embed)
                await msg_wait_please.delete()
                return

            embed = Embed(
                title=f"Добавил алиас {alias} к серверу {ip}",
                description=f"Теперь вы можете использовать вместо {ip} алиас {alias}",
                color=Color.green(),
            )

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.dns.host}:{str(info.dns.port)}")
            embed.add_field(name="Данные успешно обновлены", value='Напишите "помощь" для списка моих команд')
            embed.set_footer(text=f'Для большей информации о сервере напишите "стата {alias}"')

            await ctx.send(ctx.author.mention, embed=embed)
            await msg_wait_please.delete()
        else:
            embed = Embed(title=f"Не удалось добавить алиас {alias} к серверу {ip}", description="**Упс**", color=Color.red())

            embed.add_field(name="Не удалось добавить алиас", value="Возможно вы указали неверный айпи")
            embed.set_footer(text="Причина: Сервер не был найден в дата базе")
            await ctx.send(ctx.author.mention, embed=embed)
            await msg_wait_please.delete()


def setup(bot):
    """Добавляет класс к слушателю бота."""
    bot.add_cog(Alias(bot))
