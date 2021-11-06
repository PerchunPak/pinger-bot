from sys import version_info
from discord import Color, Embed
from discord.ext.commands import Cog, command, is_owner


class OtherCommands(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name="помощь", aliases=["help", "хэлп", "хєлп", "хелп"])
    async def help(self, ctx):
        """Это команда помощи"""
        commands = sorted([c for c in self.bot.commands if not c.hidden], key=lambda c: c.name)

        embed = Embed(
            title="Команда помощи",
            description="Я пингую сервер каждые 5 минут, и показываю его статистику! "
                        "Я довольно простой бот в использовании. Мой префикс это буквально ничего, "
                        "вам не нужно ставить префикс перед командами."
                        "\n\nВот короткий список моих команд:", color=Color.greyple())
        embed.set_footer(text="Примечание: Нет, я не пингую сервера перед тем как вы меня добавите")
        for cmd in commands:
            embed.add_field(name=cmd.name, value=cmd.help, inline=False)
        await ctx.send(embed=embed)

    @command(name="инфо", aliases=["об", "about"])
    async def about(self, ctx):
        """Немного базовой информации про меня"""
        embed = Embed(
            title=str(self.bot.user),
            description=self.bot.app_info.description + f"\n\n**ID**: {self.bot.app_info.id}", color=Color.greyple())

        embed.set_thumbnail(url=self.bot.app_info.icon_url)
        embed.add_field(name="Владелец", value=self.bot.app_info.owner)
        embed.add_field(name="Количество серверов", value=str(len(self.bot.guilds)))
        embed.add_field(name="Количество пользователей", value=str(len(self.bot.users)))
        embed.add_field(name="Язык программирования", value=f"Python {'.'.join(map(str, version_info[:-2]))}")
        embed.add_field(name="Библиотека", value="[discord.py](https://github.com/Rapptz/discord.py)")
        embed.add_field(name="Лицензия", value="[Apache License 2.0]"
                                               "(https://github.com/PerchunPak/PingerBot/blob/main/LICENSE)")
        embed.add_field(name="Открытый код", value="https://github.com/PerchunPak/PingerBot", inline=False)
        embed.set_footer(text="Примечание: Оригинальный автор не Perchun_Pak#9236, а NinjaSnail1080#8581")

        await ctx.send(embed=embed)

    @command(name="пригласить", aliases=["invite", "приглос", "приг"])
    async def invite(self, ctx):
        """Скидывает ссылку чтобы Вы могли пригласить бота на свой сервер"""
        await ctx.send('Это моя пригласительная ссылка чтобы Вы могли считать "ладно" тоже:\n'
                       f"https://discordapp.com/oauth2/authorize?client_id={self.bot.app_info.id}"
                       "&scope=bot&permissions=8")


def setup(bot):
    bot.add_cog(OtherCommands(bot))
