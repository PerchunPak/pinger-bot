"""Файл для общих методов для команд."""
from socket import gethostbyname, timeout, gaierror
from discord import Color, Embed
from mcstatus import MinecraftServer
from src.objects import ServerInfo


class MetodsForCommands:
    """Общие методы для команд.

    Attributes:
        bot: Атрибут для главного объекта бота.
    """

    def __init__(self, bot):
        """
        Args:
            bot: Главный объект бота.
        """
        self.bot = bot

    async def parse_ip(self, input_ip: str) -> ServerInfo:
        """Парсит айпи (логично).

        Args:
            input_ip: Айпи который дал юзер.

        Returns:
            Объект с информацией о сервере.
        """
        ip_from_alias = await self.bot.db.get_ip_alias(input_ip)

        if len(ip_from_alias) != 0:
            valid, alias = True, input_ip
            dns_info = MinecraftServer.lookup(str(ip_from_alias['ip']) + ":" + str(ip_from_alias['port']))
            num_ip = gethostbyname(dns_info.host)
            return ServerInfo(valid, alias, dns_info, num_ip, str(dns_info.port))
        else:
            dns_info = MinecraftServer.lookup(input_ip)
            alias_from_ip = await self.bot.db.get_alias_ip(dns_info.host, dns_info.port)
            alias = None if alias_from_ip == {} else alias_from_ip["alias"]

        try:
            num_ip = gethostbyname(dns_info.host)
            valid = True
        except gaierror: valid, num_ip = False, None

        return ServerInfo(valid, alias, dns_info, num_ip, str(dns_info.port))

    async def ping_server(self, ip: str) -> tuple:
        """Пингует сервер (очень логично).

        Args:
            ip: Айпи сервера который нужно пинговать.

        Returns:
            Объект статуса сервера и объект информации о сервере.
        """
        info = await self.parse_ip(ip)
        if not info.valid: return False, False, info

        try: status = info.dns.status()
        except (timeout, ConnectionRefusedError, gaierror, OSError): status = False

        return status, info

    @staticmethod
    async def wait_please(ctx, ip: str):
        """Отсылает сообщение "Подождите немного".

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
        """
        embed = Embed(
            title=f'Пингую {ip}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        await ctx.send(embed=embed)

    @staticmethod
    async def fail_message(ctx, ip: str, online: bool):
        """Отсылает сообщение "Не удалось выполнить команду"

        Args:
            ctx: Объект сообщения.
            ip: Айпи сервера.
            online: Онлайн сервер или нет.
        """
        embed = Embed(
            title=f'Результаты пинга {ip}',
            description=f"\n\n**{'Онлайн' if online else 'Офлайн'}**",
            color=Color.red())

        embed.add_field(name="Не удалось выполнить команду",
                        value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
        await ctx.send(ctx.author.mention, embed=embed)
