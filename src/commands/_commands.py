from socket import gethostbyname, timeout, gaierror
from discord import Color, Embed
from mcstatus import MinecraftServer
from src.objects import ServerInfo


class MetodsForCommands:
    """
    Общие методы для команд
    """

    def __init__(self, bot):
        self.bot = bot

    async def parse_ip(self, input_ip):
        ip_from_alias = await self.bot.db.get_ip_alias(input_ip)

        if len(ip_from_alias) != 0:
            valid, alias = True, input_ip
            num_ip = str(ip_from_alias[0]['numip'])[:-3]
            return ServerInfo(valid, alias, num_ip)
        else: alias = None

        try: num_ip, valid = gethostbyname(input_ip), True
        except gaierror: valid, num_ip = False, None

        return ServerInfo(valid, alias, num_ip)

    async def ping_server(self, ip):
        info = await self.parse_ip(ip)
        if not info.valid: return False, False, info

        dns_info = MinecraftServer.lookup(ip)
        try: status = dns_info.status()
        except (timeout, ConnectionRefusedError, gaierror): status = False

        return status, dns_info, info

    @staticmethod
    async def wait_please(ctx, ip):
        embed = Embed(
            title=f'Пингую {ip}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        await ctx.send(embed=embed)

    @staticmethod
    async def fail_message(ctx, ip, online):
        embed = Embed(
            title=f'Результаты пинга {ip}',
            description="\n\n**%s**" % "Онлайн" if online else "Офлайн",
            color=Color.red())

        embed.add_field(name="Не удалось пингануть сервер",
                        value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
        await ctx.send(ctx.author.mention, embed=embed)
