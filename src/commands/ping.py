"""Модуль для команды "пинг"."""
from re import sub as re_sub, IGNORECASE
from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands._commands import MetodsForCommands


class Ping(Cog):
    """Класс для команды "пинг".

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

    @command(name='пинг')
    async def ping(self, ctx, ip: str):
        """Пинг сервера и показ его основной информации.

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
        """
        await self.metods_for_commands.wait_please(ctx, ip)
        status, dns_info, info = await self.metods_for_commands.ping_server(ip)
        if status:
            embed = Embed(
                title=f'Результаты пинга {info.alias if info.alias is not None else ip}',
                description=f'Цифровое айпи: {info.ip}:{str(dns_info.port)}\n**Онлайн**',
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.ip}:{str(dns_info.port)}")
            embed.add_field(name="Время ответа", value=str(status.latency) + 'мс')
            embed.add_field(name="Используемое ПО", value=status.version.name)
            embed.add_field(name="Онлайн", value=f'{status.players.online}/{status.players.max}')
            motd_clean = re_sub(r'[\xA7|&][0-9A-FK-OR]', '', status.description, flags=IGNORECASE)
            embed.add_field(name="Мотд", value=motd_clean)
            embed.set_footer(text=f'Для получения ссылки на редактирование МОТД, напишите "мотд {ip}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            await self.metods_for_commands.fail_message(ctx, ip, online=status)


def setup(bot):
    """Добавляет класс к слушателю бота."""
    bot.add_cog(Ping(bot))
