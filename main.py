from discord.ext import commands, tasks
import discord
import asyncpg
import psutil

import datetime
import re
import os

import config
from database import PostgresController

bot_intents = discord.Intents.default()
bot_intents.members = True

bot = commands.Bot(
    command_prefix='',
    description="саншайн пингер",
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
    print('Дата-база инициализирована')

    print("\nЗашел как:")
    print(bot.user)
    print(bot.user.id)
    print("-----------------")
    print(datetime.datetime.now().strftime("%m/%d/%Y %X"))
    print("-----------------")
    print("Шардов: " + str(bot.shard_count))
    print("Серверов: " + str(len(bot.guilds)))
    print("Пользователей: " + str(len(bot.users)))
    print("-----------------\n")

    #update_db.start()
    bot.ready_for_commands = True
    bot.started_at = datetime.datetime.utcnow()
    bot.app_info = await bot.application_info()

    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(
        name='кто сколько раз сказал "ладно"', type=discord.ActivityType.competing))


# @bot.event
# async def on_message(message):
#    if not bot.ready_for_commands or message.author.bot:
#        return
#
#    if message.guild is not None:
#        for m in re.finditer(r"\b(ладно)(s\b|\b)", message.content, re.IGNORECASE):
#            if message.author.id not in bot.sunservers:
#                bot.sunservers.update(
#                    {message.author.id: {"total": 0, "id": message.author.id}})
#            bot.sunservers[message.author.id]["total"] += 1
#            bot.sunservers[0]["total"] += 1
#
#    ctx = await bot.get_context(message)
#    if ctx.valid:
#        await bot.invoke(ctx)
#    else:
#        if bot.user in message.mentions and len(message.mentions) == 2:
#            await message.channel.send(f"Вам нужно написать `@{bot.user} count <user>` чтобы "
#                                       f"получить статистику другого пользователя.\nИспользуйте"
#                                       "`@{bot.user} help` для помощи с другими командами")
#        elif bot.user in message.mentions:
#            await message.channel.send(f"Используйте `@{bot.user} help` для списка моих команд")


#@tasks.loop(minutes=5, loop=bot.loop)
#async def update_db():
#    """Обновляет ДБ каждые 5 минут"""
#
#    async with bot.pool.acquire() as conn:
#        await conn.execute("""
#            INSERT INTO sunpings (ip)
#            VALUES {} ON CONFLICT DO NOTHING
#        ;""".format(", ".join([f"({u})" for u in bot.sunpings])))
#
#        for data in bot.sunpings.copy().values():
#            await conn.execute("""
#                UPDATE sunpings
#                SET port = {}, time = {}, status = {}, players = {}
#                WHERE ip = {}
#            ;""".format(data["port"], data["time"], data["status"], data["players"], data["ip"]))
#
#        await conn.execute("""
#            INSERT INTO sunservers (id)
#            VALUES {} ON CONFLICT DO NOTHING
#        ;""".format(", ".join([f"({u})" for u in bot.sunservers])))
#
#        for data in bot.sunservers.copy().values():
#            await conn.execute("""
#                UPDATE sunservers
#                SET domen = {}, numip = {}, alias = {}, maxpl = {}
#                WHERE id = {}
#            ;""".format(data["domen"], data["numip"], data["alias"], data["maxpl"], data["id"]))


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx):
    """Перезагружает некоторые файлы бота"""

    bot.reload_extension("commands")
    await ctx.send("Файлы перезагружены")


#@bot.command(hidden=True)
#@commands.is_owner()
#async def restartdb(ctx):
#    await create_pool()
#    await ctx.send("ДБ перезагружена")


#@bot.command(hidden=True)
#@commands.is_owner()
#async def update_db(ctx):
#    update_db.cancel()
#    update_db.start()
#    await ctx.send("Отменено и запущено `update_db`")


try:
    bot.loop.run_until_complete(bot.start(config.TOKEN))
except KeyboardInterrupt:
    print("\nЗакрытие")
    bot.loop.run_until_complete(bot.change_presence(status=discord.Status.invisible))
    for e in bot.extensions.copy():
        bot.unload_extension(e)
    print("Выходим")
    bot.loop.run_until_complete(bot.logout())
finally:
    #update_db.cancel()
    bot.loop.run_until_complete(bot.pool.close())
    print("Закрыто")
