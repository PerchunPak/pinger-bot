"""
Тесты для команды "стата"
"""
from socket import timeout
from time import sleep
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from pytest import fixture, mark
from discord import Color
from mcstatus.pinger import PingResponse


class TestStatistic:
    """Класс для тестов и фикстур"""

    @fixture(scope='class')
    async def stat_online_not_added(self, event_loop, bot, database, monkeypatch_session):
        """Фикстура для проверки правильно ли бот сработает если сервер онлайн, но не добавлен"""
        def fake_server_answer(class_self=None):
            """Эмулирует ответ сервера"""
            return PingResponse(
                {
                    "description": {'text': "A Minecraft Server"},
                    "players": {"max": 20, "online": 0},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("стата 127.0.0.3")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope='class')
    async def stat_online(self, event_loop, bot, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер"""
        await database.add_server('127.0.0.4', 0, 25565)
        await database.add_record('127.0.0.4', 25565, 33)

        def fake_server_answer(class_self=None):
            """Эмулирует ответ сервера"""
            return PingResponse(
                {
                    "description": {'text': "A Minecraft Server"},
                    "players": {"max": 20, "online": 5},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("стата 127.0.0.4")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope='class')
    async def stat_alias(self, event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы"""
        await database.add_server('127.0.0.5', 0, 25565)
        await database.add_alias('тест_алиас', '127.0.0.5', 25565)

        def fake_server_answer(class_self=None):
            """Эмулирует ответ сервера"""
            return PingResponse(
                {
                    "description": {'text': "A Minecraft Server"},
                    "players": {"max": 20, "online": 5},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("стата тест_алиас")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope='class')
    async def stat_offline(self, event_loop, bot, database, monkeypatch_session):
        """Вызывает команду с пингом выключенного сервера"""
        def fake_server_answer(class_self=None):
            """Когда сервер выключен, модуль вызывает exception socket.timeout"""
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("стата 127.0.0.6")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @mark.asyncio
    async def test_server_not_added_color(self, event_loop, bot, database, stat_online_not_added):
        """Проверят цвет в ответе бота, если сервер не добавлен"""
        await database.make_tables()
        assert str(stat_online_not_added.color) == str(Color.red())

    def test_online(self, bot, database, stat_online):
        """Проверяет правильно ли бот распознает текущий онлайн"""
        online = stat_online.fields[0].value.split('/')
        assert online[0] == '5'

    def test_online_max(self, bot, database, stat_online):
        """Проверяет правильно ли бот распознает максимальный онлайн"""
        online = stat_online.fields[0].value.split('/')
        assert online[1] == '20'

    def test_record(self, bot, database, stat_online):
        """Проверяет правильно ли бот распознает рекорд онлайна"""
        assert stat_online.fields[2].value == '33'

    def test_online_yest_null(self, bot, database, stat_online):
        """Проверяет правильно ли бот распознает вчерашний онлайн, если записей об этом нету"""
        assert stat_online.fields[1].value == 'Нету информации'

    def test_color(self, bot, database, stat_online):
        """Проверят цвет в ответе бота"""
        assert str(stat_online.color) == str(Color.green())

    def test_alias_color(self, bot, stat_alias, database):
        """Проверят цвет в ответе бота, если использовать алиас"""
        assert str(stat_alias.color) == str(Color.green())

    def test_alias_numip(self, bot, stat_alias, database):
        """Проверят правильно ли бот распознает цифровое айпи, если использовать алиас"""
        assert '127.0.0.5' in stat_alias.description
        assert '25565' in stat_alias.description

    @mark.skip(reason="фича еще не добавлена")
    def test_alias_in(self, bot, ping_alias, database):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи"""
        assert 'тест_алиас' in ping_alias.title

    def test_offline_color(self, bot, database, stat_offline):
        """Проверяет цвет Embed-а когда сервер оффлайн"""
        assert str(stat_offline.color) == str(Color.red())
