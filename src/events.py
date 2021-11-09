from datetime import datetime
from socket import timeout, gaierror
from traceback import format_exception
from discord import Forbidden, NotFound
from discord import Status, ActivityType
from discord.ext.commands import Cog, NotOwner, MissingRequiredArgument
from discord.ext.commands.errors import CommandNotFound
from discord.ext.tasks import loop
from mcstatus import MinecraftServer
from src.bot import PingerBot


class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    @Cog.listener()
    async def on_connect():
        print("\nУстановлено соединение с дискордом")

    @Cog.listener()
    async def on_ready(self):
        self.bot.PingerBot = PingerBot(self.bot)
        await self.bot.PingerBot.run_db()
        print('Зашел как:\n'
              f'{self.bot.user}\n'
              f'{self.bot.user.id}\n'
              '-----------------\n'
              f'{datetime.now().strftime("%m/%d/%Y %X")}\n'
              '-----------------\n'
              f'Шардов: {str(self.bot.shard_count)}\n'
              f'Серверов: {str(len(self.bot.guilds))}\n'
              f'Пользователей: {str(len(self.bot.users))}\n'
              '-----------------')

        self.ping_servers.start()  # pylint: disable=E1101
        self.bot.app_info = await self.bot.application_info()

        await self.bot.PingerBot.set_status(Status.online, 'пинг превыше всего', ActivityType.playing)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        message.content = message.content.lower()
        ctx = await self.bot.get_context(message)
        if ctx.valid: print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        else: await message.channel.send("Используйте команду `помощь` для списка моих команд")

    @Cog.listener()
    async def on_command_error(self, ctx, exception):

        if isinstance(exception, NotOwner):
            return await ctx.send(f"Только мой Владелец, {self.bot.app_info.owner}, может использовать эту команду")

        elif isinstance(exception, MissingRequiredArgument):
            return await ctx.send(f'Не хватает необходимого аргумента `{exception.param.name}`')
        elif isinstance(exception, (Forbidden, NotFound, CommandNotFound)): return

        elif "Missing Permissions" in str(exception):
            return await ctx.send("У меня нет необходимых прав для выполнения этой команды. "
                                  "Предоставление мне разрешения администратора должно решить эту проблему")

        else:
            await ctx.send(f'```\nКоманда: {ctx.message.content}\n{exception}\n```\n'
                           'Неизвестная ошибка произошла и я не смог выполнить эту команду.\n'
                           'Я уже сообщил своему создателю')
            traceback = ''.join(format_exception(type(exception), exception, exception.__traceback__))

            if not len(traceback) > 2000:
                return await self.bot.app_info.owner.send(
                    'Юзер `%s` нашел ошибку в команде %s.\n'
                    'Traceback: \n```\n%s\n```'
                    % (str(ctx.author), ctx.command.qualified_name, traceback))
            else:
                traceback = [traceback[i:i + 2000] for i in range(0, len(traceback), 2000)]

                await self.bot.app_info.owner.send(
                    'Юзер `%s` нашел ошибку в команде %s.\n'
                    'Traceback: \n```\n%s\n```'
                    % (str(ctx.author), ctx.command.qualified_name, traceback[0]))

                for element in traceback[1:]:
                    await self.bot.app_info.owner.send(f'\n```\n{element}\n```')

    @loop(minutes=5)
    async def ping_servers(self):
        """Пингует сервера и записывает их пинги в дата базу"""

        servers = await self.bot.db.get_servers()
        for serv in servers:
            ip = str(serv['numip'])[:-3]
            port = serv['port']
            mcserver = MinecraftServer.lookup(ip + ':' + str(port))
            try:
                status = mcserver.status()
                online = True
            except (timeout, ConnectionRefusedError, gaierror): online, status = False, None

            if online:
                online_players = status.players.online
                await self.bot.db.add_ping(ip, port, online_players)

                if online_players >= serv['record'] + 1: await self.bot.db.add_record(ip, port, online_players)
        await self.bot.db.remove_too_old_pings()


def setup(bot):
    bot.add_cog(Events(bot))