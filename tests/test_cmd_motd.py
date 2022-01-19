"""Тесты для команды "мотд"."""
from socket import timeout
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture


class TestMotd:
    """Класс для тестов и фикстур."""
    @staticmethod
    @fixture(scope='class')
    async def motd_online(event_loop, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        def fake_server_answer(class_self=None) -> PingResponse:
            """Эмулирует ответ сервера.

            Args:
                class_self: Иногда при вызове метода, так же приходит аргумент `self`.

            Returns:
                Фейковый ответ сервера.
            """
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
    async def motd_alias(event_loop, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        await database.add_server('127.0.0.2', 25565, 0)
        await database.add_alias('тест_алиас', '127.0.0.2', 25565)

        def fake_server_answer(class_self=None) -> PingResponse:
            """Эмулирует ответ сервера.

            Args:
                class_self: Иногда при вызове метода, так же приходит аргумент `self`.

            Returns:
                Фейковый ответ сервера.
            """
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
    async def motd_offline(event_loop, monkeypatch_session):
        """Вызывает команду с пингом выключенного сервера.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        def fake_server_answer(class_self=None):
            """Когда сервер выключен, модуль вызывает exception socket.timeout.

            Args:
                class_self: Иногда при вызове метода, так же приходит аргумент `self`.

            Raises:
                Фейковый ответ сервера (то есть негативный).
            """
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("мотд example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    def test_color(motd_online):
        """Проверят цвет в ответе бота.

        Args:
            motd_online: Embed объект ответа.
        """
        assert str(motd_online.color) == str(Color.green())

    @staticmethod
    def test_alias_in(motd_alias):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи.

        Args:
            motd_alias: Embed объект ответа.
        """
        assert 'тест_алиас' in motd_alias.title

    @staticmethod
    def test_thumbnail_link(motd_alias):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            motd_alias: Embed объект ответа.
        """
        assert motd_alias.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.2:25565'

    @staticmethod
    def test_motd(motd_online):
        """Проверяет правильно ли бот распознает мотд.

        Args:
            motd_online: Embed объект ответа.
        """
        assert motd_online.fields[0].value == "A Minecraft Server"

    @staticmethod
    def test_url_motd(motd_online):
        """Проверяет правильно ли генерирует ссылку на редактирование мотд.

        Args:
            motd_online: Embed объект ответа.
        """
        normal_motd = motd_online.fields[1].value.replace('https://mctools.org/motd-creator?text=', '')
        normal_motd = normal_motd.replace('%0A', '\n').replace('+', ' ')
        assert normal_motd == "A Minecraft Server"

    @staticmethod
    def test_offline_color(motd_offline):
        """Проверяет цвет Embed-а когда сервер оффлайн.

        Args:
            motd_offline: Embed объект ответа.
        """
        assert str(motd_offline.color) == str(Color.red())
