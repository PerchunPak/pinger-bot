"""Тесты для команды "пинг"."""
from socket import timeout
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture


class TestPing:
    """Класс для тестов и фикстур."""
    @staticmethod
    @fixture(scope='class')
    async def ping_online(event_loop, monkeypatch_session):
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
    async def ping_alias(event_loop, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        await database.add_server('127.0.0.1', 25565, 0)
        await database.add_alias('тест_алиас', '127.0.0.1', 25565)

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
        await message("пинг тест_алиас")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def ping_offline(event_loop, monkeypatch_session):
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
        await message("пинг example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    def test_color(ping_online):
        """Проверят цвет в ответе бота.

        Args:
            ping_online: Embed объект ответа.
        """
        assert str(ping_online.color) == str(Color.green())

    @staticmethod
    def test_alias_in(ping_alias):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи.

        Args:
            ping_alias: Embed объект ответа.
        """
        assert 'тест_алиас' in ping_alias.title

    @staticmethod
    def test_alias_numip(ping_alias):
        """Проверяет правильно ли бот распознает цифровое айпи.

        Args:
            ping_alias: Embed объект ответа.
        """
        assert '127.0.0.1:25565' in ping_alias.description

    @staticmethod
    def test_thumbnail_link(ping_alias):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            ping_alias: Embed объект ответа.
        """
        assert ping_alias.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.1:25565'

    @staticmethod
    def test_ping_is_int(ping_online):
        """Проверяет является ли значение в "Время ответа" int объектом.

        Args:
            ping_online: Embed объект ответа.
        """
        # Если при переводе в int возникнет ошибка, тест провалится
        assert isinstance(int(ping_online.fields[0].value[:-2]), int)

    @staticmethod
    def test_check_version(ping_online):
        """Проверяет правильно ли бот распознает версию.

        Args:
            ping_online: Embed объект ответа.
        """
        assert ping_online.fields[1].value == "1.17.1"

    @staticmethod
    def test_online_now(ping_online):
        """Проверяет правильно ли бот распознает текущий онлайн.

        Args:
            ping_online: Embed объект ответа.
        """
        online = ping_online.fields[2].value.split('/')
        assert online[0] == "5"

    @staticmethod
    def test_online_max(ping_online):
        """Проверяет правильно ли бот распознает максимальный онлайн.

        Args:
            ping_online: Embed объект ответа.
        """
        online = ping_online.fields[2].value.split('/')
        assert online[1] == "20"

    @staticmethod
    def test_offline_color(ping_offline):
        """Проверяет цвет Embed-а когда сервер оффлайн.

        Args:
            ping_offline: Embed объект ответа.
        """
        assert str(ping_offline.color) == str(Color.red())
