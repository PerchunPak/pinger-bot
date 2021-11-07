"""
Добавляет тестовые команды которые будут использоваться самими тестами
"""
from discord.ext.commands import Cog, command
from src.commands._commands import MetodsForCommands


class Commands(Cog):
    """Команды для тестов"""

    def __init__(self, bot):
        self.bot = bot
        self.metods_for_commands = MetodsForCommands(bot)

    @command()
    async def wait_please(self, ctx, ip):
        """ Команда возвращает сообщение "Пожалуйста подождите" """
        await self.metods_for_commands.wait_please(ctx, ip)

    @command()
    async def fail_message(self, ctx, ip, online):
        """ Команда возвращает сообщение "Не удалось выполнить команду" """
        online = {
            "0": False,
            "1": True
        }[online]
        await self.metods_for_commands.fail_message(ctx, ip, online)


def setup(bot):
    bot.add_cog(Commands(bot))
