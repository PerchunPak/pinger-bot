from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands._commands import MetodsForCommands


class Motd(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.MetodsForCommands = MetodsForCommands(bot)

    @command(name='мотд')
    async def motd(self, ctx, ip):
        """Показывает мотд и ссылку на редактирование сервера"""
        await self.MetodsForCommands.wait_please(ctx, ip)
        status, dns_info, info = await self.MetodsForCommands.ping_server(ip)
        if status:
            motd = str(status.raw["description"]["text"]).replace(" ", "+")
            motd_url = motd.replace("\n", "%0A")
            embed = Embed(
                title=f'Подробное мотд сервера {ip}',
                description="Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{ip}")
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
