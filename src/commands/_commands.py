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
            ip = str(ip_from_alias['ip'])
            port = str(ip_from_alias['port'])
            return ServerInfo(valid, alias, ip, port)
        else: alias = None

        if ":" in input_ip: ip, given_port = input_ip.split(":")
        else: ip, given_port = input_ip, "25565"

        try:
            gethostbyname(ip)
            valid = True
        except gaierror: valid, ip, given_port = False, None, None

        return ServerInfo(valid, alias, ip, given_port)

    async def ping_server(self, ip: str) -> tuple:
        """Пингует сервер (очень логично).

        Args:
            ip: Айпи сервера который нужно пинговать.

        Returns:
            Объект статуса сервера, объект с DNS данными
            о сервере и информация о сервере.
        """
        info = await self.parse_ip(ip)
        if not info.valid: return False, False, info

        dns_info = MinecraftServer.lookup(info.ip + ":" + info.port)
        try: status = dns_info.status()
        except (timeout, ConnectionRefusedError, gaierror, OSError): status = False

        return status, dns_info, info

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
