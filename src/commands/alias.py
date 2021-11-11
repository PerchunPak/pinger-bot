from discord import Color, Embed
from discord.ext.commands import Cog, command
from src.commands._commands import MetodsForCommands


class Alias(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.metods_for_commands = MetodsForCommands(bot)

    @command(name='алиас')
    async def alias(self, ctx, alias, ip):
        """Добавление алиаса к серверу"""
        await self.metods_for_commands.wait_please(ctx, ip)
        status, dns_info, info = await self.metods_for_commands.ping_server(ip)  # pylint: disable=W0612
        if info.valid: database_server = await self.bot.db.get_server(info.ip, dns_info.port)
        else: database_server = []
        if len(database_server) != 0:
            name = info.alias if info.alias is not None else ip
            if ctx.author.id != database_server[0]['owner']:
                embed = Embed(
                    title=f'Вы не владелец сервера {name}',
                    description=f'Только владелец может изменить/добавить алиас сервера {name}',
                    color=Color.red())

                embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.ip}:{str(dns_info.port)}")
                embed.add_field(name="Ошибка", value='Вы не владелец')
                embed.set_footer(text=f'Для большей информации о сервере напишите "стата {name}"')

                return await ctx.send(ctx.author.mention, embed=embed)

            await self.bot.db.add_alias(alias, info.ip, dns_info.port)
            embed = Embed(
                title=f'Добавил алиас {alias} к серверу {ip}',
                description=f'Теперь вы можете использовать вместо {ip} алиас {alias}',
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.ip}:{str(dns_info.port)}")
            embed.add_field(name="Данные успешно обновлены",
                            value='Напишите "помощь" для списка моих команд')
            embed.set_footer(text=f'Для большей информации о сервере напишите "стата {alias}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f'Не удалось добавить алиас {alias} к серверу {ip}',
                description="**Упс**",
                color=Color.red())

            embed.add_field(name="Не удалось добавить алиас",
                            value='Возможно вы указали неверный айпи')
            embed.set_footer(text='**Причина:** Сервер не был найден в дата базе')
            await ctx.send(ctx.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(Alias(bot))
