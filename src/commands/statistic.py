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


class Statistic(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name='стата')
    async def statistic(self, ctx, server):
        """Статистика сервера"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = Embed(
            title=f'Получаю данные сервера {server}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        await ctx.send(embed=embed)
        ip_from_alias = await self.bot.db.get_ip_alias(server)
        if len(ip_from_alias) != 0:
            server = str(ip_from_alias[0]['numip'])[0:-3] + ':' + str(ip_from_alias[0]['port'])
        mcserver = MinecraftServer.lookup(server)
        try:
            status = mcserver.status()
            valid = True
        except (timeout, ConnectionRefusedError): valid, status = True, None
        except gaierror: valid, status = False, None
        if valid:
            num_ip = gethostbyname(mcserver.host)
            database_server = await self.bot.db.get_server(num_ip, mcserver.port)
        else: database_server, num_ip = [], None
        if valid and len(database_server) != 0:
            if database_server[0]['alias'] is not None:
                server = database_server[0]['alias']
            embed = Embed(
                title=f'Статистика сервера {server}',
                description=f"Цифровое айпи: {num_ip}:{str(mcserver.port)}\n**Онлайн**",
                color=Color.green())

            yesterday_25h = datetime.now() - timedelta(hours=25)
            yesterday_23h = datetime.now() - timedelta(hours=23)
            pings = await self.bot.db.get_pings(num_ip, mcserver.port)
            online_yest = None
            for ping in pings:  # ищет пинги в радиусе двух часов сутки назад
                if (yesterday_23h > ping['time'] > yesterday_25h) and \
                        (yesterday_23h.day >= ping['time'].day >= yesterday_25h.day):
                    online_yest = ping['players']
            if online_yest is None: online_yest = 'Нету информации'

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{mcserver.host}:{str(mcserver.port)}")
            embed.add_field(name="Текущий онлайн", value=str(status.players.online) + '/' + str(status.players.max))
            embed.add_field(name="Онлайн сутки назад в это же время", value=online_yest)
            embed.add_field(name="Рекорд онлайна за всё время", value=str(database_server[0]['record']))
            embed.set_footer(text=f'Для большей информации о сервере напишите "пинг {server}"')

            pings = await self.bot.db.get_pings(num_ip, mcserver.port)
            if len(pings) <= 20: return await ctx.send(ctx.author.mention + ', слишком мало информации для графика.',
                                                       embed=embed)
            fig, ax = subplots()
            arr_online = []
            arr_time = []
            for ping in pings:
                arr_online.append(int(ping['players']))
                arr_time.append(ping['time'])
            my_fmt = DateFormatter('%H:%M')
            ax.xaxis.set_major_formatter(my_fmt)
            ax.plot(arr_time, arr_online)

            xlabel('Время')
            ylabel('Онлайн')
            title('Статистика сервера ' + server)

            file_name = num_ip + '_' + str(mcserver.port) + '.png'
            try: mkdir('./plots/')
            except FileExistsError: pass
            fig.savefig('./plots/' + file_name)
            file = File('./plots/' + file_name, filename=file_name)
            embed.set_image(url='attachment://' + file_name)

            await ctx.send(ctx.author.mention, embed=embed, file=file)

            await sleep(10)
            try: remove('./plots/' + file_name)
            except (PermissionError, FileNotFoundError): pass
        else:
            embed = Embed(
                title=f'Статистика сервера {server}',
                description="**Офлайн**",
                color=Color.red())

            embed.add_field(name="Не удалось получить статистику сервера",
                            value='Возможно вы указали неверный айпи/алиас, или сервер еще не добавлен')
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Statistic(bot))

