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
            ip = str(ip_from_alias[0]['ip'])[:-3]
            return ServerInfo(valid, alias, ip)
        else: alias = None

        try: ip, valid = gethostbyname(input_ip), True
        except gaierror: valid, ip = False, None

        return ServerInfo(valid, alias, ip)

    async def ping_server(self, ip):
        info = await self.parse_ip(ip)
        if not info.valid: return False, False, info

        dns_info = MinecraftServer.lookup(ip)
        try: status = dns_info.status()
        except (timeout, ConnectionRefusedError, gaierror, OSError): status = False

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
            description=f"\n\n**{'Онлайн' if online else 'Офлайн'}**",
            color=Color.red())

        embed.add_field(name="Не удалось выполнить команду",
                        value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
        await ctx.send(ctx.author.mention, embed=embed)
