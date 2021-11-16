"""Файл для команды "добавить" и ничего больше."""
from asyncpg.exceptions import UniqueViolationError
from discord import Color, Embed
from discord.ext.commands import Cog, command, is_owner
from src.commands.commands_ import MetodsForCommands


class AddServer(Cog):
    """Класс для команды "добавить".

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

    @command(name='добавить')
    @is_owner()
    async def add_server(self, ctx, ip: str):
        """Добавление сервера в бота.

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
        """
        await self.metods_for_commands.wait_please(ctx, ip)
        status, dns_info, info = await self.metods_for_commands.ping_server(ip)
        if status:
            try: await self.bot.db.add_server(info.ip, dns_info.port, ctx.author.id)
            except UniqueViolationError:  # сервер уже добавлен
                embed = Embed(
                    title=f'Не удалось добавить сервер {ip}',
                    description="**Онлайн**",
                    color=Color.red())

                embed.add_field(name="Не удалось добавить сервер",
                                value='Сервер уже добавлен')
                return await ctx.send(ctx.author.mention, embed=embed)

            embed = Embed(
                title=f'Добавил сервер {ip}',
                description=f"Цифровое айпи: {info.ip}:{str(dns_info.port)}\n**Онлайн**",
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.ip}:{str(dns_info.port)}")
            embed.add_field(name="Сервер успешно добавлен",
                            value='Напишите "помощь" для получения большей информации о серверах')
            embed.set_footer(text=f'Теперь вы можете использовать "стата {ip}" или "алиас (алиас) {ip}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            await self.metods_for_commands.fail_message(ctx, ip, online=status)


def setup(bot):
    """Добавляет класс к слушателю бота."""
    bot.add_cog(AddServer(bot))
