from asyncio import sleep
from datetime import datetime, timedelta
from os import mkdir, remove
from re import sub as re_sub, IGNORECASE
from socket import gethostbyname, timeout, gaierror
from sys import version_info
from asyncpg.exceptions import UniqueViolationError
from discord import Color, Embed, File
from discord.ext.commands import Cog, command, is_owner
from matplotlib.dates import DateFormatter
from matplotlib.pyplot import subplots, xlabel, ylabel, title
from mcstatus import MinecraftServer


class Motd(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name='мотд')
    async def motd(self, ctx, ip):
        """Показывает мотд и ссылку на редактирование сервера"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = Embed(
            title=f'Получаю данные сервера {ip}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        await ctx.send(embed=embed)
        ip_from_alias = await self.bot.db.get_ip_alias(ip)
        if len(ip_from_alias) != 0:
            ip = str(ip_from_alias[0]['numip'])[0:-3] + ':' + str(ip_from_alias[0]['port'])
        server = MinecraftServer.lookup(ip)
        try:
            status = server.status()
            online = True
        except (timeout, ConnectionRefusedError, gaierror): online, status = False, None
        if online:
            motd = str(status.raw['description']['text']).replace(' ', '+')
            motd_url = motd.replace('\n', '%0A')
            embed = Embed(
                title=f'Подробное мотд сервера {ip}',
                description="Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{server.host}:{str(server.port)}")
            embed.add_field(name="Мотд", value=f"{status.description}")
            embed.add_field(name="Ссылка на редактирование", value="https://mctools.org/motd-creator?text=" + motd_url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f'Подробное мотд сервера {ip}',
                description="Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=Color.red())

            embed.add_field(name="Не удалось получить данные с сервера",
                            value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
            await ctx.send(ctx.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(Motd(bot))
