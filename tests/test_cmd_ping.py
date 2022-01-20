"""
Тесты для команды "пинг"
"""
from socket import timeout
from time import sleep
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from pytest import fixture, mark
from discord import Color
from mcstatus.pinger import PingResponse


class TestPing:
    """Класс для тестов и фикстур"""

    @fixture(scope="class")
    async def ping_online(self, event_loop, bot, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер"""

        def fake_server_answer(class_self=None):
            """Эмулирует ответ сервера"""
            return PingResponse(
                {
                    "description": {"text": "A Minecraft Server"},
                    "players": {"max": 20, "online": 5},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("пинг example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def ping_alias(self, event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы"""
        await database.add_server("127.0.0.1", 0, 25565)
        await database.add_alias("тест_алиас", "127.0.0.1", 25565)

        def fake_server_answer(class_self=None):
            """Эмулирует ответ сервера"""
            return PingResponse(
                {
                    "description": {"text": "A Minecraft Server"},
                    "players": {"max": 20, "online": 0},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("пинг тест_алиас")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def ping_offline(self, event_loop, bot, database, monkeypatch_session):
        """Вызывает команду с пингом выключенного сервера"""

        def fake_server_answer(class_self=None):
            """Когда сервер выключен, модуль вызывает exception socket.timeout"""
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("пинг example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    def test_color(self, bot, ping_online, database):
        """Проверят цвет в ответе бота"""
        assert str(ping_online.color) == str(Color.green())

    def test_check_version(self, bot, ping_online, database):
        """Проверяет правильно ли бот распознает версию"""
        assert ping_online.fields[1].value == "1.17.1"

    def test_online_now(self, bot, ping_online, database):
        """Проверяет правильно ли бот распознает текущий онлайн"""
        online = ping_online.fields[2].value.split("/")
        assert online[0] == "5"

    def test_online_max(self, bot, ping_online, database):
        """Проверяет правильно ли бот распознает максимальный онлайн"""
        online = ping_online.fields[2].value.split("/")
        assert online[1] == "20"

    def test_alias_color(self, bot, ping_alias, database):
        """Проверяет цвет Embed-а при использовании алиаса"""
        assert str(ping_alias.color) == str(Color.green())

    def test_alias_numip(self, bot, ping_alias, database):
        """Проверяет правильно ли бот распознает цифровое айпи"""
        assert "127.0.0.1" in ping_alias.description
        assert "25565" in ping_alias.description

    @mark.skip(reason="фича еще не добавлена")  # TODO добавить эту фичу
    def test_alias_in(self, bot, ping_alias, database):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи"""
        assert "тест_алиас" in ping_alias.title

    def test_offline_color(self, bot, ping_offline, database):
        """Проверяет цвет Embed-а когда сервер оффлайн"""
        assert str(ping_offline.color) == str(Color.red())
