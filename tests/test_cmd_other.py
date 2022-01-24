"""Тесты для других команд."""
from sys import version_info
from discord.ext.test import message, get_message, get_embed
from pytest import fixture


class TestOtherCommands:
    """Класс для тестов и фикстур."""

    @fixture(scope="class")
    async def help_cmd(self, event_loop):
        """Фикстура для проверки команды "помощь".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Dict из Embed объекта ответа.
        """
        await message("помощь")
        return get_embed().to_dict()

    @fixture(scope="class")
    async def about(self, event_loop):
        """Фикстура для проверки команды "инфо".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Embed объект ответа.
        """
        await message("инфо")
        return get_embed()

    @fixture(scope="class")
    async def invite(self, event_loop):
        """Фикстура для проверки команды "пригласить".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Сообщение ответа.
        """
        await message("пригласить")
        return get_message()

    def test_help_commands(self, bot, help_cmd):
        """Проверяет правильно ли бот распознает команды.

        Args:
            bot: Главный объект бота.
            help_cmd: Dict из Embed объекта ответа.
        """
        i = 0
        commands = sorted([c for c in bot.commands if not c.hidden], key=lambda c: c.name)
        for field in help_cmd["fields"]:
            assert {"inline": False, "name": commands[i].name, "value": commands[i].help[0]} == field
            i += 1

    def test_about_description(self, bot, about):
        """Проверят правильно ли бот распознает описание в дискорде.

        Args:
            bot: Главный объект бота.
            about: Embed объект ответа.
        """
        assert bot.app_info.description in about.description

    def test_about_id(self, bot, about):
        """Проверят правильно ли бот распознает свой айди.

        Args:
            bot: Главный объект бота.
            about: Embed объект ответа.
        """
        assert str(bot.app_info.id) in about.description

    def test_about_owner(self, bot, about):
        """Проверят правильно ли бот распознает владельца.

        Args:
            bot: Главный объект бота.
            about: Embed объект ответа.
        """
        assert str(bot.app_info.owner) == about.fields[0].value

    def test_about_count_servers_int(self, about):
        """Проверят int ли количество серверов.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет непонятно из-за чего тест проваливается.

        Args:
            about: Embed объект ответа.
        """
        assert isinstance(int(about.fields[1].value), int)

    def test_about_count_users_int(self, about):
        """Проверят int ли количество пользователей.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет непонятно из-за чего тест проваливается.

        Args:
            about: Embed объект ответа.
        """
        assert isinstance(int(about.fields[2].value), int)

    def test_about_python_version(self, about):
        """Проверят правильно ли бот распознает версию Python.

        Args:
            about: Embed объект ответа.
        """
        assert ".".join(map(str, version_info[:3])) in about.fields[3].value

    def test_invite_link(self, bot, invite):
        """Проверят правильно ли бот создает ссылку-приглашение.

        Args:
            bot: Главный объект бота.
            invite: Сообщение ответа.
        """
        assert f"https://discordapp.com/oauth2/authorize?client_id={bot.app_info.id}&scope=bot&permissions=8" in invite.content
