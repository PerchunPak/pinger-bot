"""Тесты для команды "добавить"."""
from socket import timeout
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture


class TestAddServer:
    """Класс для тестов и фикстур."""

    @staticmethod
    @fixture(scope="class")
    async def fake_is_owner(event_loop, bot, monkeypatch_session):
        """Обманывает проверку на владельца бота.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.
        """

        async def fake_is_owner_func(*args, **kwargs) -> bool:
            """Эмулирует ответ функции проверки автора.

            Args:
                args: Заглушка для аргументов.
                kwargs: Тоже заглушка.

            Returns:
                True.
            """
            return True

        monkeypatch_session.setattr(bot, "is_owner", fake_is_owner_func)

    @staticmethod
    @fixture(scope="class")
    async def add_online(event_loop, fake_is_owner, monkeypatch_session):
        """Основная фикстура для тестов, добавляет онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            fake_is_owner: Обманывает проверку на владельца бота.
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
                    "description": {"text": "A Minecraft Server"},
                    "players": {"max": 20, "online": 5},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("добавить 127.0.0.33")
        embed = get_embed()
        while str(embed.color) == str(
            Color.orange()
        ):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope="class")
    async def add_offline(event_loop, fake_is_owner, monkeypatch_session):
        """Пытается добавить офлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            fake_is_owner: Обманывает проверку на владельца бота.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """

        def fake_server_answer(class_self=None) -> PingResponse:
            """Эмулирует ответ сервера.

            Args:
                class_self: Иногда при вызове метода, так же приходит аргумент `self`.

            Returns:
                Фейковый ответ сервера (то есть негативный).
            """
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await message("добавить example.com")
        embed = get_embed()
        while str(embed.color) == str(
            Color.orange()
        ):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope="class")
    async def add_already(event_loop, fake_is_owner, database, monkeypatch_session):
        """Пытается добавить уже добавленный сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            fake_is_owner: Обманывает проверку на владельца бота.
            database: Объект дата базы.
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
                    "description": {"text": "A Minecraft Server"},
                    "players": {"max": 20, "online": 5},
                    "version": {"name": "1.17.1", "protocol": 756},
                }
            )

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        await database.add_server("127.0.0.34", 25565, 0)
        await message("добавить 127.0.0.34")
        embed = get_embed()
        while str(embed.color) == str(
            Color.orange()
        ):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    def test_online_color(add_online):
        """Проверят цвет в ответе бота.

        Args:
            add_online: Embed объект ответа.
        """
        assert str(add_online.color) == str(Color.green())

    @staticmethod
    def test_online_ip_in_title(add_online):
        """Проверяет что есть айпи в title.

        Args:
            add_online: Embed объект ответа.
        """
        assert "127.0.0.33" in add_online.title

    @staticmethod
    def test_online_num_ip_description(add_online):
        """Проверяет есть ли цифровое айпи в description.

        Args:
            add_online: Embed объект ответа.
        """
        assert "127.0.0.33:25565" in add_online.description

    @staticmethod
    def test_online_thumbnail_link(add_online):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            add_online: Embed объект ответа.
        """
        assert (
            add_online.thumbnail.url == "https://api.mcsrvstat.us/icon/127.0.0.33:25565"
        )

    @staticmethod
    def test_offline_color(add_offline):
        """Проверят цвет в офлайн ответе бота.

        Args:
            add_offline: Embed объект ответа.
        """
        assert str(add_offline.color) == str(Color.red())

    @staticmethod
    def test_already_color(add_already):
        """Проверят цвет в ответе бота, если сервер уже добавлен.

        Args:
            add_already: Embed объект ответа.
        """
        assert str(add_already.color) == str(Color.red())

    @staticmethod
    def test_already_ip_in_title(add_already):
        """Проверяет что есть айпи в title.
        Args:
            add_already: Embed объект ответа.
        """
        assert "127.0.0.34" in add_already.title
