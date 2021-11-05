from socket import gethostbyname
from discord import Color, Embed
from discord.ext.commands import Cog, command
from mcstatus import MinecraftServer


class Alias(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name='алиас')
    async def alias(self, ctx, alias, server):
        """Добавление алиаса к серверу"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = Embed(
            title=f'Получаю данные сервера {server}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        await ctx.send(embed=embed)
        mcserver = MinecraftServer.lookup(server)
        num_ip = gethostbyname(mcserver.host)
        database_server = await self.bot.db.get_server(num_ip, mcserver.port)
        if len(database_server) != 0:
            if ctx.author.id != database_server[0]['owner']:
                embed = Embed(
                    title=f'Вы не владелец сервера {server}',
                    description=f'Только владелец может изменять алиас сервера {server}',
                    color=Color.red())

                embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{mcserver.host}:{str(mcserver.port)}")
                embed.add_field(name="Ошибка",
                                value='Вы не владелец')
                embed.set_footer(text=f'Для большей информации о сервере напишите "стата {server}"')

                return await ctx.send(ctx.author.mention, embed=embed)

            await self.bot.db.add_alias(alias, num_ip, mcserver.port)
            embed = Embed(
                title=f'Записал алиас {alias} к серверу {server}',
                description=f'Теперь вы можете использовать вместо {server} алиас {alias}',
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{mcserver.host}:{str(mcserver.port)}")
            embed.add_field(name="Данные успешно обновлены",
                            value='Напишите "помощь" для получения большей информации о серверах')
            embed.set_footer(text=f'Для большей информации о сервере напишите "стата {alias}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f'Не удалось добавить алиас {alias} к серверу {server}',
                description="**Упс**",
                color=Color.red())

            embed.add_field(name="Не удалось добавить алиас",
                            value='Возможно вы указали неверный айпи')
            await ctx.send(ctx.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(Alias(bot))
