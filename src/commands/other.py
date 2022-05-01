"""Модуль для других команд."""
from sys import version_info
import subprocess
from discord import Color, Embed
from discord.ext.commands import Cog, command, is_owner
from src.commands.commands_ import MetodsForCommands


class OtherCommands(Cog):
    """Класс для команды "мотд".

    Attributes:
        bot: Атрибут для главного объекта бота.
        metods_for_commands: Инициализированный класс MetodsForCommands.
    """

    def __init__(self, bot):
        """
        Args:
            bot: Главный объект бота.
        """
        self.bot = bot
        self.metods_for_commands = MetodsForCommands(bot)

    @command(name="помощь", aliases=["help", "хэлп", "хєлп", "хелп"])
    async def help(self, ctx):
        """Это команда помощи.

        Args:
            ctx: Объект сообщения.
        """
        commands = sorted([c for c in self.bot.commands if not c.hidden], key=lambda c: c.name)

        embed = Embed(
            title="Команда помощи",
            description="Я пингую сервер каждые 5 минут, и показываю его статистику! "
            "Я довольно простой бот в использовании. Мой префикс это буквально ничего, "
            "вам не нужно ставить префикс перед командами."
            "\n\nВот короткий список моих команд:",
            color=Color.greyple(),
        )
        embed.set_footer(text="Примечание: Нет, я не пингую сервера перед тем как вы меня добавите")
        for cmd in commands:
            cmd.help = cmd.help.split("\n")
            embed.add_field(name=cmd.name, value=cmd.help[0], inline=False)
        await ctx.send(embed=embed)

    @command(name="инфо", aliases=["об", "about"])
    async def about(self, ctx):
        """Немного базовой информации про меня.

        Args:
            ctx: Объект сообщения.
        """
        embed = Embed(
            title=str(self.bot.user),
            description=self.bot.app_info.description + f"\n\n**ID**: {self.bot.app_info.id}",
            color=Color.greyple(),
        )

        embed.set_thumbnail(url=self.bot.app_info.icon_url)
        embed.add_field(name="Владелец", value=self.bot.app_info.owner)
        embed.add_field(name="Количество серверов", value=str(len(self.bot.guilds)))
        embed.add_field(name="Количество пользователей", value=str(len(self.bot.users)))
        embed.add_field(name="Язык программирования", value=f"Python {'.'.join(map(str, version_info[:-2]))}")
        embed.add_field(name="Библиотека", value="[discord.py](https://github.com/Rapptz/discord.py)")
        embed.add_field(
            name="Лицензия", value="[Apache License 2.0]" "(https://github.com/PerchunPak/PingerBot/blob/main/LICENSE)"
        )
        embed.add_field(name="Открытый код", value="https://github.com/PerchunPak/PingerBot", inline=False)
        embed.set_footer(text="Примечание: Вы можете предлагать любые идеи в ЛС Perchun_Pak#9236")
        await ctx.send(embed=embed)

    @command(name="пригласить", aliases=["invite", "приглос", "приг"])
    async def invite(self, ctx):
        """Скидывает ссылку чтобы Вы могли пригласить бота на свой сервер.

        Args:
            ctx: Объект сообщения.
        """
        await ctx.send(
            "Это моя пригласительная ссылка чтобы Вы могли пинговать сервера тоже:\n"
            f"https://discordapp.com/oauth2/authorize?client_id={self.bot.app_info.id}"
            "&scope=bot&permissions=8"
        )

    @command(name="владелец", aliases=["who_owner", "owner", "кто_владелец", "кто владелец"])
    async def who_owner(self, ctx, server_name):
        """Показывает владельца сервера.

        Args:
            ctx: Объект сообщения.
            server_name: Имя сервера (айпи или алиас).
        """
        info = await self.metods_for_commands.parse_ip(server_name)

        if info.valid:
            database_server = await self.bot.db.get_server(info.dns.host, info.dns.port)
        else:
            database_server = {}

        if info.valid and len(database_server) != 0:
            owner_obj = self.bot.get_user(database_server["owner"])
            owner = "@" + owner_obj.display_name + "#" + owner_obj.discriminator

            embed = Embed(
                title=f"Владелец сервера {info.alias if info.alias is not None else server_name}",
                description="Это " + owner,
                color=Color.green(),
            )

            embed.set_footer(
                text="Для большей информации о сервере напишите "
                f'"стата {info.alias if info.alias is not None else server_name}"'
            )

            return await ctx.send(embed=embed)
        else:
            embed = Embed(
                title=f"Владелец сервера {server_name}",
                color=Color.red(),
            )

            embed.add_field(
                name="Не удалось выполнить команду", value="Возможно вы указали неверный айпи, или сервер не добавлен"
            )
            return await ctx.send(embed=embed)

    @command(name="version", aliases=["commit", "v", "ver", "версия", "вер", "в", "комит", "коммит"], hiden=True)
    async def get_bot_version(self, ctx):
        """Отправляет пользователю коммит взятый из папки .git.

        Args:
            ctx: Объект сообщения.

        Returns:
            Объект сообщения отправленного пользователю в ответ.
        """
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            embed = Embed(
                title="Версия бота",
                color=Color.red(),
            )
            embed.add_field(name="GIT не доступен", value="К сожалению, бот не может получить доступ к GIT")
            return await ctx.send(embed=embed)

        embed = Embed(
            title="Версия бота",
            color=Color.green(),
        )
        embed.add_field(name="Хэш коммита", value=commit[:7])
        embed.set_footer(text=commit)

        return await ctx.send(embed=embed)

    @command(name="execute_sql", aliases=["sql", "sql_execute", "execute"], hidden=True)
    @is_owner()
    async def execute_sql(self, ctx, *sql):
        """Выполняет SQL запрос в базу данных. Только для владельца.

        Args:
            ctx: Объект сообщения.
            sql: SQL для обработки.
        """
        result = await self.bot.db.pool.fetch(" ".join(sql))
        ret = "Результат: \n"
        for record in result:
            ret += str(dict(record)) + "\n"
        if ret == "Результат: \n":
            ret = "Выполнено успешно."
        await ctx.send(ret)


def setup(bot):
    """Добавляет класс к слушателю бота."""
    bot.add_cog(OtherCommands(bot))
