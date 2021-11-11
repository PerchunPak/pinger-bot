"""
Тесты для команды "алиас"
"""
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from pytest import fixture, mark


class TestAlias:
    """Класс для тестов и фикстур"""
    @staticmethod
    @fixture(scope='class')
    async def alias_added_not_owner(event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов если сервер добавлен, но юзер не владелец"""
        await database.add_server('127.0.0.8', 0, 25565)
        await message("алиас тест1 127.0.0.8")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def alias_added(event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов если алиас добавлен"""
        test_user = None
        for user in bot.users:
            if user.bot: continue
            test_user = user
        await database.add_server('127.0.0.9', test_user.id, 25565)
        await message("алиас тест2 127.0.0.9")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def alias_not_added(event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов если сервер не добавлен"""
        await message("алиас тест3 127.0.0.10")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @mark.asyncio
    async def test_is_added_to_db(event_loop, bot, database, alias_added):
        """Проверяет добавился ли алиас в дата базу"""
        ip_from_alias = await database.get_ip_alias('тест2')
        ip_from_alias = str(ip_from_alias[0]['ip']) + ':' + str(ip_from_alias[0]['port'])
        assert ip_from_alias == '127.0.0.9:25565'

    @staticmethod
    def test_not_owner(bot, database, alias_added_not_owner):
        """Проверяет правильно ли бот понимает кто владелец"""
        assert alias_added_not_owner.fields[0].value == 'Вы не владелец'

    @staticmethod
    def test_color(bot, database, alias_added):
        """Проверят цвет в ответе бота"""
        assert str(alias_added.color) == str(Color.green())

    @staticmethod
    def test_thumbnail_link(bot, alias_added, database):
        """Проверяет ссылку в маленькой картинке справо сверху"""
        assert alias_added.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.9:25565'

    @staticmethod
    def test_not_added(bot, database, alias_not_added):
        """Проверяет правильно ли бот распознает если сервере еще не добавлен"""
        assert 'не был найден в дата базе' in alias_not_added.footer.text
