from re import sub as re_sub, IGNORECASE
from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands._commands import MetodsForCommands


class Ping(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.MetodsForCommands = MetodsForCommands(bot)

    @command(name='пинг')
    async def ping(self, ctx, ip):
        """Пинг сервера и показ его основной информации"""
        await self.MetodsForCommands.wait_please(ctx, ip)
        ping_info = await self.MetodsForCommands.ping_server(ip)
        if ping_info:
            alias = ping_info["info"]["alias"]
            embed = Embed(
                title=f'Результаты пинга {alias if alias is not None else ip}',
                description=f'Цифровое айпи: {ping_info["info"]["num_ip"]}\n**Онлайн**',
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{ip}")
            embed.add_field(name="Время ответа", value=str(ping_info["status"].latency) + 'мс')
            embed.add_field(name="Используемое ПО", value=ping_info["status"].version.name)
            embed.add_field(name="Онлайн",
                            value=f'{ping_info["status"].players.online}/{ping_info["status"].players.max}')
            motd_clean = re_sub(r'[\xA7|&][0-9A-FK-OR]', '', ping_info["status"].description, flags=IGNORECASE)
            embed.add_field(name="Мотд", value=motd_clean)
            embed.set_footer(text=f'Для получения ссылки на редактирование МОТД, напишите "мотд {ip}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            await self.MetodsForCommands.fail_message(ctx, ip, online=False)


def setup(bot):
    bot.add_cog(Ping(bot))
