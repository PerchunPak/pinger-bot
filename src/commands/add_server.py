from asyncpg.exceptions import UniqueViolationError
from discord import Color, Embed
from discord.ext.commands import Cog, command, is_owner
from src.commands._commands import MetodsForCommands


class AddServer(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.metods_for_commands = MetodsForCommands(bot)

    @command(name='добавить')
    @is_owner()
    async def add_server(self, ctx, ip):
        """Добавление сервера в бота"""
        await self.metods_for_commands.wait_please(ctx, ip)
        status, dns_info, info = await self.metods_for_commands.ping_server(ip)
        if status:
            name = info.alias if info.alias is not None else ip
            try: await self.bot.db.add_server(info.num_ip, ctx.author.id, dns_info.port)
            except UniqueViolationError:  # сервер уже добавлен
                embed = Embed(
                    title=f'Не удалось добавить сервер {name}',
                    description="**Онлайн**",
                    color=Color.red())

                embed.add_field(name="Не удалось добавить сервер",
                                value='Сервер уже добавлен')
                return await ctx.send(ctx.author.mention, embed=embed)

            embed = Embed(
                title=f'Добавил сервер {name}',
                description=f"Цифровое айпи: {info.num_ip}:{str(dns_info.port)}\n**Онлайн**",
                color=Color.green())

            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{info.num_ip}:{str(dns_info.port)}")
            embed.add_field(name="Сервер успешно добавлен",
                            value='Напишите "помощь" для получения большей информации о серверах')
            embed.set_footer(text=f'Теперь вы можете использовать "стата {name}" или "алиас (алиас) {ip}"')

            await ctx.send(ctx.author.mention, embed=embed)
        else:
            await self.metods_for_commands.fail_message(ctx, ip, online=status)


def setup(bot):
    bot.add_cog(AddServer(bot))
