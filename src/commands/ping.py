from re import sub as re_sub, IGNORECASE
from socket import gethostbyname, timeout, gaierror
from discord import Color, Embed
from discord.ext.commands import Cog, command
from mcstatus import MinecraftServer


class Ping(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name='пинг')
    async def ping(self, ctx, ip):
        """Пинг сервера и показ его основной информации"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = Embed(
            title=f'Пингую {ip}...',
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
            num_ip = gethostbyname(server.host)
            embed = Embed(
                title=f'Результаты пинга {ip}',
                description=f"Цифровое айпи: {num_ip}:{str(server.port)}\n**Онлайн**",
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{server.host}:{str(server.port)}")
            embed.add_field(name="Время ответа", value=str(status.latency) + 'мс')
            embed.add_field(name="Используемое ПО", value=status.version.name)
            embed.add_field(name="Онлайн", value=f"{status.players.online}/{status.players.max}")
            motd_clean = re_sub(r'[\xA7|&][0-9A-FK-OR]', '', status.description, flags=IGNORECASE)
            embed.add_field(name="Мотд", value=motd_clean)
            embed.set_footer(text=f'Для получения ссылки на редактирование МОТД, напишите "мотд {ip}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f'Результаты пинга {ip}',
                description="\n\n**Офлайн**",
                color=Color.red())

            embed.add_field(name="Не удалось пингануть сервер",
                            value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
            await ctx.send(ctx.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(Ping(bot))
