"""
Тесты для других команд
"""
from discord.ext.test import message, get_message, get_embed
from pytest import fixture
from sys import version_info


class TestOtherCommands:
    """Класс для тестов и фикстур"""

    @fixture(scope="class")
    async def help_cmd(self, event_loop, bot):
        """Фикстура для проверки команды "помощь"."""
        await message("помощь")
        return get_embed().to_dict()

    @fixture(scope="class")
    async def about(self, event_loop, bot):
        """Фикстура для проверки команды "инфо"."""
        await message("инфо")
        return get_embed()

    @fixture(scope="class")
    async def invite(self, event_loop, bot):
        """Фикстура для проверки команды "пригласить"."""
        await message("пригласить")
        return get_message()

    def test_help_commands(self, bot, help_cmd):
        """Проверяет правильно ли бот распознает команды."""
        i = 0
        commands = sorted(
            [c for c in bot.commands if not c.hidden], key=lambda c: c.name
        )
        for field in help_cmd["fields"]:
            assert {
                "inline": False,
                "name": commands[i].name,
                "value": commands[i].help,
            } == field
            i += 1

    def test_about_description(self, bot, about):
        """Проверят правильно ли бот распознает описание в дискорде."""
        assert bot.app_info.description in about.description

    def test_about_id(self, bot, about):
        """Проверят правильно ли бот распознает свой айди."""
        assert str(bot.app_info.id) in about.description

    def test_about_owner(self, bot, about):
        """Проверят правильно ли бот распознает владельца."""
        assert str(bot.app_info.owner) == about.fields[0].value

    def test_about_count_servers_int(self, bot, about):
        """
        Проверят int ли количество серверов.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет не понятно из за чего тест проваливается.
        """
        assert isinstance(int(about.fields[1].value), int)

    def test_about_count_users_int(self, bot, about):
        """
        Проверят int ли количество пользователей.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет не понятно из за чего тест проваливается.
        """
        assert isinstance(int(about.fields[2].value), int)

    def test_about_python_version(self, bot, about):
        """Проверят правильно ли бот распознает версию Python."""
        assert ".".join(map(str, version_info[:3])) in about.fields[3].value

    def test_invite_link(self, bot, invite):
        """Проверят правильно ли бот создает ссылку-приглашение."""
        assert (
            f"https://discordapp.com/oauth2/authorize?client_id={bot.app_info.id}&scope=bot&permissions=8"
            in invite.content
        )
