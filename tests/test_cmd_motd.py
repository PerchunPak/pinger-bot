"""
Тесты для команды "мотд"
"""
from socket import timeout
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture


class TestMotd:
    """Класс для тестов и фикстур"""

    @staticmethod
    @fixture(scope='class')
    async def motd_online(event_loop, bot, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер"""
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
        await message("мотд example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def motd_alias(event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы"""
        await database.add_server('127.0.0.2', 0, 25565)
        await database.add_alias('тест_алиас', '127.0.0.2', 25565)

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
        await message("мотд тест_алиас")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def motd_offline(event_loop, bot, database, monkeypatch_session):
        """Вызывает команду с пингом выключенного сервера"""
        def fake_server_answer(class_self=None):
            """Когда сервер выключен, модуль вызывает exception socket.timeout"""
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("мотд example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    def test_color(bot, motd_online, database):
        """Проверят цвет в ответе бота"""
        assert str(motd_online.color) == str(Color.green())

    @staticmethod
    def test_alias_in(bot, motd_alias, database):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи"""
        assert 'тест_алиас' in motd_alias.title

    @staticmethod
    def test_thumbnail_link(bot, motd_alias, database):
        """Проверяет ссылку в маленькой картинке справо сверху"""
        assert 'https://api.mcsrvstat.us/icon/127.0.0.2:25565' == motd_alias.thumbnail.url

    @staticmethod
    def test_motd(bot, motd_online, database):
        """Проверяет правильно ли бот распознает мотд"""
        assert motd_online.fields[0].value == "A Minecraft Server"

    @staticmethod
    def test_url_motd(bot, motd_online, database):
        """Проверяет правильно ли генерирует ссылку на редактирование мотд"""
        normal_motd = motd_online.fields[1].value.replace('https://mctools.org/motd-creator?text=', '')
        normal_motd = normal_motd.replace('%0A', '\n').replace('+', ' ')
        assert normal_motd == "A Minecraft Server"

    @staticmethod
    def test_offline_color(bot, motd_offline, database):
        """Проверяет цвет Embed-а когда сервер оффлайн"""
        assert str(motd_offline.color) == str(Color.red())