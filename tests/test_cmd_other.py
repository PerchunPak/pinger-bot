"""
Тесты для других команд
"""
from sys import version_info
from discord.ext.test import message, get_message, get_embed
from pytest import fixture


class TestOtherCommands:
    """Класс для тестов и фикстур"""

    @staticmethod
    @fixture(scope='class')
    async def help_cmd(event_loop):
        """Фикстура для проверки команды "помощь"."""
        await message("помощь")
        return get_embed().to_dict()

    @staticmethod
    @fixture(scope='class')
    async def about(event_loop):
        """Фикстура для проверки команды "инфо"."""
        await message("инфо")
        return get_embed()

    @staticmethod
    @fixture(scope='class')
    async def invite(event_loop):
        """Фикстура для проверки команды "пригласить"."""
        await message("пригласить")
        return get_message()

    @staticmethod
    def test_help_commands(bot, help_cmd):
        """Проверяет правильно ли бот распознает команды."""
        i = 0
        commands = sorted([c for c in bot.commands if not c.hidden], key=lambda c: c.name)
        for field in help_cmd['fields']:
            assert {'inline': False, 'name': commands[i].name, 'value': commands[i].help} == field
            i += 1

    @staticmethod
    def test_about_description(bot, about):
        """Проверят правильно ли бот распознает описание в дискорде."""
        assert bot.app_info.description in about.description

    @staticmethod
    def test_about_id(bot, about):
        """Проверят правильно ли бот распознает свой айди."""
        assert str(bot.app_info.id) in about.description

    @staticmethod
    def test_about_owner(bot, about):
        """Проверят правильно ли бот распознает владельца."""
        assert str(bot.app_info.owner) == about.fields[0].value

    @staticmethod
    def test_about_count_servers_int(about):
        """
        Проверят int ли количество серверов.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет не понятно из за чего тест проваливается.
        """
        assert isinstance(int(about.fields[1].value), int)

    @staticmethod
    def test_about_count_users_int(about):
        """
        Проверят int ли количество пользователей.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет не понятно из за чего тест проваливается.
        """
        assert isinstance(int(about.fields[2].value), int)

    @staticmethod
    def test_about_python_version(about):
        """Проверят правильно ли бот распознает версию Python."""
        assert '.'.join(map(str, version_info[:3])) in about.fields[3].value

    @staticmethod
    def test_invite_link(bot, invite):
        """Проверят правильно ли бот создает ссылку-приглашение."""
        assert f"https://discordapp.com/oauth2/authorize?client_id={bot.app_info.id}&scope=bot&permissions=8" \
               in invite.content
