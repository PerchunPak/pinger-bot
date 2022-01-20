"""
Тесты для команды "алиас"
"""
from time import sleep
from discord.ext.test import message, get_embed
from pytest import fixture, mark
from discord import Color


class TestAlias:
    """Класс для тестов и фикстур"""

    @fixture(scope="class")
    async def alias_added_not_owner(self, event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов если сервер добавлен, но юзер не владелец"""
        await database.add_server("127.0.0.7", 0, 25565)
        await message("алиас тест1 127.0.0.7")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def alias_added(self, event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов если алиас добавлен"""
        test_user = None
        for user in bot.users:
            if user.bot:
                continue
            test_user = user
        await database.add_server("127.0.0.8", test_user.id, 25565)
        await message("алиас тест2 127.0.0.8")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def alias_not_added(self, event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов если сервер не добавлен"""
        await message("алиас тест3 127.0.0.9")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @mark.asyncio
    async def test_is_added_to_db(self, event_loop, bot, database, alias_added):
        """Проверяет добавился ли алиас в дата базу"""
        ip_from_alias = await database.get_ip_alias("тест2")
        ip_from_alias = str(ip_from_alias[0]["numip"])[0:-3] + ":" + str(ip_from_alias[0]["port"])
        assert ip_from_alias == "127.0.0.8:25565"

    def test_color(self, bot, database, alias_added):
        """Проверят цвет в ответе бота"""
        assert str(alias_added.color) == str(Color.green())

    def test_not_owner(self, bot, database, alias_added_not_owner):
        """Проверяет правильно ли бот понимает кто владелец"""
        assert alias_added_not_owner.fields[0].value == "Вы не владелец"

    def test_not_owner_color(self, bot, database, alias_added_not_owner):
        """Проверяет цвет Embed-а если алиас добавлен, и юзер не владелец"""
        assert str(alias_added_not_owner.color) == str(Color.red())

    def test_not_added(self, bot, database, alias_not_added):
        """Проверяет правильно ли бот распознает если сервере еще не добавлен"""
        assert alias_not_added.fields[0].name == "Не удалось добавить алиас"

    def test_not_added_color(self, bot, database, alias_not_added):
        """Проверяет цвет Embed-а когда сервер не добавлен"""
        assert str(alias_not_added.color) == str(Color.red())
