"""Добавляет тестовые команды которые будут использоваться самими тестами."""
from discord.ext.commands import Cog, command
from src.commands.commands_ import MetodsForCommands


class Commands(Cog):
    """Команды для тестов.

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

    @command()
    async def wait_please(self, ctx, ip: str):
        """Команда возвращает сообщение "Пожалуйста подождите".

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
        """
        await self.metods_for_commands.wait_please(ctx, ip)

    @command()
    async def fail_message(self, ctx, ip: str, online: str):
        """Команда возвращает сообщение "Не удалось выполнить команду".

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
            online: 1 или 0, онлайн сервера
        """
        online = bool(int(online))
        await self.metods_for_commands.fail_message(ctx, ip, online)


def setup(bot):
    """Добавляет класс к слушателю бота."""
    bot.add_cog(Commands(bot))
