"""Тесты для команды "алиас"."""
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from pytest import fixture, mark


class TestAlias:
    """Класс для тестов и фикстур."""
    @staticmethod
    @fixture(scope='class')
    async def alias_added_not_owner(event_loop, database):
        """Фикстура для тестов если сервер добавлен, но юзер не владелец.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.

        Returns:
            Embed объект ответа.
        """
        await database.add_server('127.0.0.8', 25565, 0)
        await message("алиас тест1 127.0.0.8")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def alias_added(event_loop, bot, database):
        """Фикстура для тестов если алиас добавлен.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота
            database: Объект дата базы.

        Returns:
            Embed объект ответа.
        """
        test_user = None
        for user in bot.users:
            if user.bot: continue
            test_user = user
        await database.add_server('127.0.0.9', 25565, test_user.id)
        await message("алиас тест2 127.0.0.9")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def alias_not_added(event_loop):
        """Фикстура для тестов если сервер не добавлен.

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Embed объект ответа.
        """
        await message("алиас тест3 not_valid")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def alias_already_added(event_loop, bot, database):
        """Фикстура для тестов если алиас уже добавлен.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота
            database: Объект дата базы.

        Returns:
            Embed объект ответа.
        """
        test_user = None
        for user in bot.users:
            if user.bot: continue
            test_user = user
        await database.add_server('127.0.0.10', 25565, test_user.id)
        await database.add_server('random_server.com', 25565, 0)
        await database.add_alias("тест4", 'random_server.com', 25565)
        await message("алиас тест4 127.0.0.10")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @mark.asyncio
    async def test_is_added_to_db(event_loop, database, alias_added):
        """Проверяет добавился ли алиас в дата базу.

        Args:
            event_loop: Обязательная фикстура для async тестов.
            database: Объект дата базы.
            alias_added: Embed объект ответа.
        """
        ip_from_alias = await database.get_ip_alias('тест2')
        ip_from_alias = str(ip_from_alias['ip']) + ':' + str(ip_from_alias['port'])
        assert ip_from_alias == '127.0.0.9:25565'

    @staticmethod
    def test_not_owner(alias_added_not_owner):
        """Проверяет правильно ли бот понимает кто владелец.

        Args:
            alias_added_not_owner: Embed объект ответа.
        """
        assert alias_added_not_owner.fields[0].value == 'Вы не владелец'

    @staticmethod
    def test_color(alias_added):
        """Проверят цвет в ответе бота.

        Args:
            alias_added: Embed объект ответа.
        """
        assert str(alias_added.color) == str(Color.green())

    @staticmethod
    def test_thumbnail_link(alias_added):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            alias_added: Embed объект ответа.
        """
        assert alias_added.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.9:25565'

    @staticmethod
    def test_not_added(alias_not_added):
        """Проверяет правильно ли бот распознает если сервере еще не добавлен.

        Args:
            alias_not_added: Embed объект ответа.
        """
        assert 'не был найден в дата базе' in alias_not_added.footer.text

    @staticmethod
    def test_already_color(alias_already_added):
        """Проверяет цвет если алиас уже добавлен.

        Args:
             alias_already_added: Embed объект ответа.
        """
        assert str(alias_already_added.color) == str(Color.red())

    @staticmethod
    def test_already_thumbnail_link(alias_already_added):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            alias_already_added: Embed объект ответа.
        """
        assert alias_already_added.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.10:25565'

    @staticmethod
    def test_already_alias_in_title(alias_already_added):
        """Проверяет есть ли алиас в title если алиас уже добавлен

        Args:
            alias_already_added: Embed объект ответа.
        """
        assert "тест4" in alias_already_added.title
