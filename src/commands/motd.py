from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands._commands import MetodsForCommands


class Motd(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.metods_for_commands = MetodsForCommands(bot)

    @command(name='мотд')
    async def motd(self, ctx, ip):
        """Показывает мотд и ссылку на редактирование сервера"""
        await self.metods_for_commands.wait_please(ctx, ip)
        status, dns_info, info = await self.metods_for_commands.ping_server(ip)  # pylint: disable=W0612
        if status:
            embed = Embed(
                title=f'Подробное мотд сервера {info.alias if info.alias is not None else ip}',
                description="Эта команда дает возможность скопировать мотд и вставить на свой сервер",
                color=Color.green())

            motd = str(status.raw["description"]["text"]).replace(" ", "+")
            motd_url = motd.replace("\n", "%0A")

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.num_ip}:{str(dns_info.port)}")
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
