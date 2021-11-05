from socket import gethostbyname, timeout, gaierror
from discord import Color, Embed
from mcstatus import MinecraftServer


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
            num_ip = str(ip_from_alias[0]['numip'])[:-3] + ':' + str(ip_from_alias[0]['port'])
            return {"valid": valid, "alias": alias, "num_ip": num_ip, "input_ip": input_ip}
        else: alias = None

        try: num_ip, valid = gethostbyname(input_ip), True
        except gaierror: valid, num_ip = False, None

        return {"valid": valid, "alias": alias, "num_ip": num_ip, "input_ip": input_ip}

    async def ping_server(self, ip):
        info = await self.parse_ip(ip)
        if not info["valid"]: return False

        server = MinecraftServer.lookup(ip)
        try: status = server.status()
        except (timeout, ConnectionRefusedError, gaierror): status = None
        if status is None: return False

        return {"status": status, "dns_info": server, "info": info}

    @staticmethod
    async def wait_please(ctx, ip):
        embed = Embed(
            title=f'Пингую {ip}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        return await ctx.send(embed=embed)

    @staticmethod
    async def fail_message(ctx, ip, online):
        embed = Embed(
            title=f'Результаты пинга {ip}',
            description="\n\n**%s**" % "Онлайн" if online else "Офлайн",
            color=Color.red())

        embed.add_field(name="Не удалось пингануть сервер",
                        value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
        await ctx.send(ctx.author.mention, embed=embed)
