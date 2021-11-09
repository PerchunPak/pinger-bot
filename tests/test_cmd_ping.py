"""
Тесты для команды "пинг"
"""
from socket import timeout
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture


class TestPing:
    """Класс для тестов и фикстур"""

    @staticmethod
    @fixture(scope='class')
    async def ping_online(event_loop, bot, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер"""
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
        await message("пинг example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def ping_alias(event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы"""
        await database.add_server('127.0.0.1', 0, 25565)
        await database.add_alias('тест_алиас', '127.0.0.1', 25565)

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
        await message("пинг тест_алиас")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def ping_offline(event_loop, bot, database, monkeypatch_session):
        """Вызывает команду с пингом выключенного сервера"""
        def fake_server_answer(class_self=None):
            """Когда сервер выключен, модуль вызывает exception socket.timeout"""
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("пинг example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    def test_color(bot, ping_online, database):
        """Проверят цвет в ответе бота"""
        assert str(ping_online.color) == str(Color.green())

    @staticmethod
    def test_alias_in(bot, ping_alias, database):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи"""
        assert 'тест_алиас' in ping_alias.title

    @staticmethod
    def test_alias_numip(bot, ping_alias, database):
        """Проверяет правильно ли бот распознает цифровое айпи"""
        assert '127.0.0.1:25565' in ping_alias.description

    @staticmethod
    def test_thumbnail_link(bot, ping_alias, database):
        """Проверяет ссылку в маленькой картинке справо сверху"""
        assert ping_alias.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.1:25565'

    @staticmethod
    def test_ping_is_int(bot, ping_online, database):
        """Проверяет является ли значение в "Время ответа" int объектом"""
        # Если при переводе в int возникнет ошибка, тест провалится
        assert isinstance(int(ping_online.fields[0].value[:-2]), int)

    @staticmethod
    def test_check_version(bot, ping_online, database):
        """Проверяет правильно ли бот распознает версию"""
        assert ping_online.fields[1].value == "1.17.1"

    @staticmethod
    def test_online_now(bot, ping_online, database):
        """Проверяет правильно ли бот распознает текущий онлайн"""
        online = ping_online.fields[2].value.split('/')
        assert online[0] == "5"

    @staticmethod
    def test_online_max(bot, ping_online, database):
        """Проверяет правильно ли бот распознает максимальный онлайн"""
        online = ping_online.fields[2].value.split('/')
        assert online[1] == "20"

    @staticmethod
    def test_offline_color(bot, ping_offline, database):
        """Проверяет цвет Embed-а когда сервер оффлайн"""
        assert str(ping_offline.color) == str(Color.red())
