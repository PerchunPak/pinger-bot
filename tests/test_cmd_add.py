"""Тесты для команды "добавить"."""
from socket import timeout
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture

# TODO Переделать fake_is_owner в общую фикстуру


class TestAddServer:
    """Класс для тестов и фикстур."""
    @staticmethod
    @fixture(scope='class')
    async def add_online(event_loop, bot, monkeypatch_session):
        """Основная фикстура для тестов, добавляет онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        def fake_server_answer(class_self=None) -> PingResponse:
            """Эмулирует ответ сервера.

            Args:
                class_self: Иногда при вызове функции, так же приходит аргумент `self`.

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

        async def fake_is_owner(class_self=None, author_id=None) -> bool:
            """Эмулирует ответ функции проверки автора.

            Args:
                class_self: Иногда при вызове функции, так же приходит аргумент `self`.
                author_id: Айди пользователя который приходит оригинальной функции.

            Returns:
                True.
            """
            return True

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        monkeypatch_session.setattr(bot, "is_owner", fake_is_owner)
        await message("добавить 127.0.0.33")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def add_offline(event_loop, bot, monkeypatch_session):
        """Пытается добавить офлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        def fake_server_answer(class_self=None) -> PingResponse:
            """Эмулирует ответ сервера.

            Args:
                class_self: Иногда при вызове функции, так же приходит аргумент `self`.

            Returns:
                Фейковый ответ сервера (то есть негативный).
            """
            raise timeout

        async def fake_is_owner(class_self=None, author_id=None) -> bool:
            """Эмулирует ответ функции проверки автора.

            Args:
                class_self: Иногда при вызове функции, так же приходит аргумент `self`.
                author_id: Айди пользователя который приходит оригинальной функции.

            Returns:
                True.
            """
            return True

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        monkeypatch_session.setattr(bot, "is_owner", fake_is_owner)
        await message("добавить 127.0.0.34")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
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
        assert add_online.thumbnail.url == 'https://api.mcsrvstat.us/icon/127.0.0.33:25565'

    @staticmethod
    def test_offline_color(add_offline):
        """Проверят цвет в офлайн ответе бота.

        Args:
            add_offline: Embed объект ответа.
        """
        assert str(add_offline.color) == str(Color.red())
