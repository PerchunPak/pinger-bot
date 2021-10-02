from discord.ext.commands import Bot, is_owner
from discord.ext.tasks import loop
from discord import Intents, Status, Activity, ActivityType, Client
from datetime import datetime
from config import TOKEN
from database import PostgresController
from mcstatus import MinecraftServer
from socket import timeout

bot_intents = Intents.default()
bot_intents.members = True

bot = Bot(
    command_prefix='',
    description="Пингер бот",
    case_insensitive=False,
    help_command=None,
    status=Status.invisible,
    intents=bot_intents,
    fetch_offline_members=True
)

bot.ready_for_commands = False
bot.load_extension("commands")
bot.load_extension("error_handlers")


@bot.event
async def on_connect():
    print("\nУстановлено соединение с дискордом")


@bot.event
async def on_ready():
    pg_controller = await PostgresController.get_instance()
    await pg_controller.make_tables()
    bot.db = pg_controller
    print('Дата-база инициализирована\n'

          '\nЗашел как:\n'
          f'{bot.user}\n'
          f'{bot.user.id}\n'
          '-----------------\n'
          f'{datetime.now().strftime("%m/%d/%Y %X")}\n'
          '-----------------\n'
          f'Шардов: {str(bot.shard_count)}\n'
          f'Серверов: {str(len(bot.guilds))}\n'
          f'Пользователей: {str(len(bot.users))}\n'
          '-----------------')

    ping_servers.start()
    bot.ready_for_commands = True
    bot.started_at = datetime.utcnow()
    bot.app_info = await bot.application_info()

    await bot.change_presence(status=Status.online, activity=Activity(
        name='пинг превыше всего', type=ActivityType.playing))


@bot.event
async def on_message(message):
    if not bot.ready_for_commands or message.author.bot:
        return

    ctx = await bot.get_context(message)
    if ctx.valid: await bot.invoke(ctx)
    else:
        if bot.user in message.mentions: await message.channel.send(
            "Используйте команду `помощь` для списка моих команд")


@loop(minutes=5, loop=bot.loop)
async def ping_servers():
    """Пингует сервера и записывает их пинги в датабазу"""

    servers = await bot.db.get_servers()
    for serv in servers:
        ip = str(serv['numip'])[:-3]
        port = serv['port']
        mcserver = MinecraftServer.lookup(ip + ':' + str(port))
        try:
            status = mcserver.status()
            online = True
        except timeout: online = False
        except ConnectionRefusedError: online = False

        if not online:
            await bot.db.add_ping(ip, port, -1)
        else:
            onlinePlayers = status.players.online
            await bot.db.add_ping(ip, port, onlinePlayers)

            if onlinePlayers >= serv['record'] + 1: await bot.db.add_record(ip, port, onlinePlayers)


@bot.command(hidden=True)
@is_owner()
async def reload(ctx):
    """Перезагружает некоторые файлы бота"""

    bot.reload_extension("commands")
    bot.reload_extension("error_handlers")
    await ctx.send("Файлы перезагружены")


@bot.command(hidden=True)
@is_owner()
async def restartpings(ctx):
    ping_servers.cancel()
    ping_servers.start()
    await ctx.send("Отменено и запущено `ping_servers`")


try:
    bot.loop.run_until_complete(bot.start(TOKEN))
except KeyboardInterrupt:
    print("\nЗакрытие")
    bot.loop.run_until_complete(
        bot.change_presence(status=Status.invisible))
    for e in bot.extensions.copy():
        bot.unload_extension(e)
    print("Выходим")
    bot.loop.run_until_complete(Client.close(bot))
finally:
    ping_servers.cancel()
    print("Закрыто")
