from socket import gethostbyname, timeout, gaierror
from asyncpg.exceptions import UniqueViolationError
from discord import Color, Embed
from discord.ext.commands import Cog, command, is_owner
from mcstatus import MinecraftServer


class AddServer(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name='добавить')
    @is_owner()
    async def add_server(self, ctx, server):
        """Добавление сервера в бота"""
        print(f'{ctx.author.name} использовал команду "{ctx.message.content}"')
        embed = Embed(
            title=f'Получаю данные сервера {server}...',
            description="Подождите немного, я вас упомяну когда закончу",
            color=Color.orange())
        await ctx.send(embed=embed)
        mcserver = MinecraftServer.lookup(server)
        try:
            mcserver.status()
            online = True
        except (timeout, ConnectionRefusedError, gaierror): online = False
        if online:
            num_ip = gethostbyname(mcserver.host)
            try: await self.bot.db.add_server(num_ip, ctx.author.id, mcserver.port)
            except UniqueViolationError:  # сервер уже добавлен
                embed = Embed(
                    title=f'Не удалось добавить сервер {server}',
                    description="**Онлайн**",
                    color=Color.red())

                embed.add_field(name="Не удалось добавить сервер",
                                value='Сервер уже добавлен')
                return await ctx.send(ctx.author.mention, embed=embed)

            embed = Embed(
                title=f'Добавил сервер {server}',
                description=f"Цифровое айпи: {num_ip}:{str(mcserver.port)}\n**Онлайн**",
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{mcserver.host}:{str(mcserver.port)}")
            embed.add_field(name="Сервер успешно добавлен",
                            value='Напишите "помощь" для получения большей информации о серверах')
            embed.set_footer(text=f'Теперь вы можете использовать "стата {server}" или "алиас (алиас) {server}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = Embed(
                title=f'Не удалось добавить сервер {server}',
                description="**Офлайн**",
                color=Color.red())

            embed.add_field(name="Не удалось добавить сервер",
                            value='Возможно вы указали неверный айпи, или сервер сейчас выключен')
            await ctx.send(ctx.author.mention, embed=embed)


def setup(bot):
    bot.add_cog(AddServer(bot))
