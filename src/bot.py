from shutil import rmtree
from socket import timeout, gaierror
from discord import Status, Client
from discord.ext.commands import is_owner, command
from discord.ext.tasks import loop
from mcstatus import MinecraftServer
from config import TOKEN


class PingerBot:
    def __init__(self, bot):
        self.bot = bot

    def run(self):
        self.load_extensions()

        try:
            self.bot.loop.run_until_complete(self.bot.start(TOKEN))
        except KeyboardInterrupt:
            print("\nЗакрытие")
            self.bot.loop.run_until_complete(self.bot.change_presence(status=Status.invisible))
            for e in self.bot.extensions.copy(): self.bot.unload_extension(e)
            try: rmtree('./plots/')
            except FileNotFoundError: pass
            print("Выходим")
            self.bot.loop.run_until_complete(Client.close(self.bot))
        finally:
            print("Закрыто")

    def load_extensions(self):
        self.bot.load_extension("src.commands")
        self.bot.load_extension("src.error_handlers")

    def loops(self):
        bot = self.bot

        @loop(minutes=5, loop=self.bot.loop)
        async def ping_servers():
            """Пингует сервера и записывает их пинги в дата базу"""

            servers = await bot.db.get_servers()
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
                    await bot.db.add_ping(ip, port, online_players)

                    if online_players >= serv['record'] + 1: await bot.db.add_record(ip, port, online_players)
            await bot.db.remove_too_old_pings()

        self.ping_servers = ping_servers

    @command(hidden=True)
    @is_owner()
    async def restart_pings(self, ctx):
        self.ping_servers.cancel()
        self.ping_servers.start()
        await ctx.send("Отменено и запущено `ping_servers`")
