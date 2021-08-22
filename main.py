from discord.ext import commands, tasks
import discord
import asyncpg
import psutil

import datetime
import re
import os

import config
from database import PostgresController
import mcstatus
from socket import timeout as socket_timeout

bot_intents = discord.Intents.default()
bot_intents.members = True

bot = commands.Bot(
    command_prefix='',
    description="Пингер бот",
    case_insensitive=False,
    help_command=None,
    status=discord.Status.invisible,
    intents=bot_intents,
    fetch_offline_members=True
)

bot.process = psutil.Process(os.getpid())
bot.ready_for_commands = False
bot.load_extension("commands")


@bot.event
async def on_connect():
    print("\nУстановлено соединение с дискордом")


@bot.event
async def on_ready():
    pg_controller = await PostgresController.get_instance()
    await ping_servers()
    print('Дата-база инициализирована\n'

          '\nЗашел как:\n'
          f'{bot.user}\n'
          f'{bot.user.id}\n'
          '-----------------\n'
          f'{datetime.datetime.now().strftime("%m/%d/%Y %X")}\n'
          '-----------------\n'
          f'Шардов: {str(bot.shard_count)}\n'
          f'Серверов: {str(len(bot.guilds))}\n'
          f'Пользователей: {str(len(bot.users))}\n'
          '-----------------')

    bot.ready_for_commands = True
    bot.started_at = datetime.datetime.utcnow()
    bot.app_info = await bot.application_info()

    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(
        name='пинг превыше всего', type=discord.ActivityType.playing))


@tasks.loop(minutes=5, loop=bot.loop)
async def ping_servers():
    """Пингует сервера и записывает их пинги в датабазу"""

    pg_controller = await PostgresController.get_instance()
    servers = await pg_controller.get_servers()
    for serv in servers:
        ip = str(serv['numip'])[:-3]
        port = serv['port']
        mcserver = mcstatus.MinecraftServer.lookup(ip+':'+str(port))
        try:
            status = mcserver.status()
            online = True
        except socket_timeout: online = False

        if not online:
            await pg_controller.add_ping(ip, port, -1)
            return
        onlinePlayers = status.players.online
        await pg_controller.add_ping(ip, port, onlinePlayers)

        if onlinePlayers >= serv['record']+1: await pg_controller.add_record(ip,port, onlinePlayers)



@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx):
    """Перезагружает некоторые файлы бота"""

    bot.reload_extension("commands")
    await ctx.send("Файлы перезагружены")


try:  # TODO наконец то пофиксить это
    bot.loop.run_until_complete(bot.start(config.TOKEN))
except KeyboardInterrupt:
    print("\nЗакрытие")
    bot.loop.run_until_complete(
        bot.change_presence(status=discord.Status.invisible))
    for e in bot.extensions.copy():
        bot.unload_extension(e)
    print("Выходим")
    bot.loop.run_until_complete(bot.logout())
finally:
    bot.loop.run_until_complete(bot.pool.close())
    print("Закрыто")
