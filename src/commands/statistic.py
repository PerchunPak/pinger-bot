from asyncio import sleep
from datetime import datetime, timedelta
from os import mkdir, remove
from discord import Color, Embed, File
from discord.ext.commands import Cog, command
from matplotlib.dates import DateFormatter
from matplotlib.pyplot import subplots, xlabel, ylabel, title
from src.commands._commands import MetodsForCommands


class Statistic(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.MetodsForCommands = MetodsForCommands(bot)

    @command(name='стата')
    async def statistic(self, ctx, ip):
        """Статистика сервера"""
        await self.MetodsForCommands.wait_please(ctx, ip)
        status, dns_info, info = await self.MetodsForCommands.ping_server(ip)

        if info.valid: database_server = await self.bot.db.get_server(info.num_ip, dns_info.port)
        else: database_server = []

        if info.valid and len(database_server) != 0:
            embed = Embed(
                title=f'Статистика сервера {info.alias if info.alias is not None else ip}',
                description=f"Цифровое айпи: {info.num_ip}:{str(dns_info.port)}\n"
                            f"**{'Онлайн' if status else 'Офлайн'}**",
                color=Color.green())

            pings = await self.bot.db.get_pings(info.num_ip, dns_info.port)
            online_yest = await self.get_yest_ping(pings)

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{ip}")
            embed.add_field(name="Текущий онлайн", value=str(status.players.online) + '/' + str(status.players.max))
            embed.add_field(name="Онлайн сутки назад в это же время", value=online_yest)
            embed.add_field(name="Рекорд онлайна за всё время", value=str(database_server[0]['record']))
            embed.set_footer(text=f'Для большей информации о сервере напишите "пинг {ip}"')

            if len(pings) <= 20:
                return await ctx.send(ctx.author.mention + ', слишком мало информации для графика.', embed=embed)

            fig = self.create_plot(pings, info, ip)
            await self.send_and_cache_plot(fig, info, dns_info, embed, ctx)
        else:
            await self.MetodsForCommands.fail_message(ctx, ip, online=status)

    @staticmethod
    async def get_yest_ping(pings):
        yesterday_25h = datetime.now() - timedelta(hours=25)
        yesterday_23h = datetime.now() - timedelta(hours=23)
        online_yest = 'Нету информации'
        for ping in pings:  # ищет пинги в радиусе двух часов сутки назад
            if (yesterday_23h > ping['time'] > yesterday_25h) and \
                    (yesterday_23h.day >= ping['time'].day >= yesterday_25h.day):
                online_yest = ping['players']
        return online_yest

    @staticmethod
    def create_plot(pings, info, ip):
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
        title('Статистика сервера ' + info.alias if info.alias is not None else ip)

        return fig

    @staticmethod
    async def send_and_cache_plot(fig, info, dns_info, embed, ctx):
        file_name = info.num_ip + '_' + str(dns_info.port) + '.png'
        try: mkdir('./plots/')
        except FileExistsError: pass
        fig.savefig('./plots/' + file_name)
        file = File('./plots/' + file_name, filename=file_name)
        embed.set_image(url='attachment://' + file_name)

        await ctx.send(ctx.author.mention, embed=embed, file=file)

        await sleep(10)
        try: remove('./plots/' + file_name)
        except (PermissionError, FileNotFoundError): pass


def setup(bot):
    bot.add_cog(Statistic(bot))
