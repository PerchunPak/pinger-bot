"""Тесты для команды "стата"."""
from socket import timeout
from datetime import datetime, timedelta
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed, get_message
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture
from sqlalchemy import insert
from src.commands.statistic import Statistic


class TestStatistic:
    """Класс для тестов и фикстур."""

    @fixture(scope="class")
    async def stat_online(self, event_loop, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        database.add_server("127.0.0.3", 25565, 0)
        database.add_record("127.0.0.3", 25565, 33)

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
        await message("стата 127.0.0.3")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def stat_online_as_msg(self, event_loop, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Сообщение ответа.
        """
        database.add_server("127.0.0.4", 25565, 0)
        database.add_record("127.0.0.4", 25565, 33)

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
        await message("стата 127.0.0.4")
        msg = get_message()
        while str(msg.embeds[0].color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            msg = get_message()

        return msg

    @fixture(scope="class")
    async def stat_alias(self, event_loop, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        database.add_server("127.0.0.5", 25565, 0)
        database.add_alias("тест_алиас", "127.0.0.5", 25565)
        yesterday = datetime.now() - timedelta(hours=24)
        database.execute(insert(database.t.sp).values(ip="127.0.0.5", port=25565, time=yesterday, players=12), commit=True)

        # Генерирует 25 пингов
        i = 0
        args = []
        while i <= 25:
            time = datetime.now() - timedelta(minutes=i * 10)
            args.append({"ip": "127.0.0.5", "port": 25565, "time": time, "players": i})
            i += 1
        database.execute(insert(database.t.sp), params=args, commit=True)

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
        await message("стата тест_алиас")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def stat_offline(self, event_loop, monkeypatch_session):
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
        await message("стата not_valid")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def stat_valid_offline(self, event_loop, monkeypatch_session):
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
        await message("стата example.com")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)  # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @fixture(scope="class")
    async def get_yest_ping(self, event_loop, database):
        """Вызывает метод получения вчерашнего пинга.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.

        Returns:
            Ответ метода `Statistic.get_yest_ping`.
        """
        yesterday = datetime.now() - timedelta(hours=24)
        database.execute(insert(database.t.sp).values(ip="127.0.0.7", port=25565, time=yesterday, players=12), commit=True)

        # Генерирует 25 пингов
        i = 0
        args = []
        while i <= 25:
            time = datetime.now() - timedelta(minutes=i * 10)
            args.append({"ip": "127.0.0.7", "port": 25565, "time": time, "players": i})
            i += 1
        database.execute(insert(database.t.sp), params=args)

        pings = database.get_pings("127.0.0.7", 25565)
        return await Statistic.get_yest_ping(pings)

    @fixture(scope="class")
    async def get_yest_ping_null(self, event_loop, database):
        """Вызывает метод получения вчерашнего пинга.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.

        Returns:
            Ответ метода `Statistic.get_yest_ping`.
        """
        pings = database.get_pings("127.0.0.8", 25565)
        return await Statistic.get_yest_ping(pings)

    def test_online_color(self, stat_online):
        """Проверят цвет в ответе бота.

        Args:
            stat_online: Embed объект ответа.
        """
        assert str(stat_online.color) == str(Color.green())

    def test_offline_color(self, stat_offline):
        """Проверят цвет в ответе бота, если сервер офлайн и/или не валидный.

        Args:
            stat_offline: Embed объект ответа.
        """
        assert str(stat_offline.color) == str(Color.red())

    def test_valid_offline_color(self, stat_valid_offline):
        """Проверят цвет в ответе бота, если сервер офлайн и валидный.

        Args:
            stat_valid_offline: Embed объект ответа.
        """
        assert str(stat_valid_offline.color) == str(Color.red())

    def test_alias_in(self, stat_alias):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert "тест_алиас" in stat_alias.title

    def test_alias_numip(self, stat_alias):
        """Проверят правильно ли бот распознает цифровое айпи, если использовать алиас.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert "127.0.0.5:25565" in stat_alias.description

    def test_online_in_description(self, stat_online):
        """Проверят правильно ли бот пишет онлайн сервера.

        Args:
            stat_online: Embed объект ответа.
        """
        assert "**Онлайн**" in stat_online.description

    def test_offline_in_description(self, stat_offline):
        """Проверят правильно ли бот пишет офлайн сервера.

        Args:
            stat_offline: Embed объект ответа.
        """
        assert "**Офлайн**" in stat_offline.description

    def test_valid_offline_in_description(self, stat_valid_offline):
        """Проверят правильно ли бот пишет офлайн сервера.

        Args:
            stat_valid_offline: Embed объект ответа.
        """
        assert "**Офлайн**" in stat_valid_offline.description

    def test_thumbnail_link(self, stat_alias):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert stat_alias.thumbnail.url == "https://api.mcsrvstat.us/icon/127.0.0.5:25565"

    def test_online(self, stat_online):
        """Проверяет правильно ли бот распознает текущий онлайн.

        Args:
            stat_online: Embed объект ответа.
        """
        online = stat_online.fields[0].value.split("/")
        assert online[0] == "5"

    def test_online_max(self, stat_online):
        """Проверяет правильно ли бот распознает максимальный онлайн.

        Args:
            stat_online: Embed объект ответа.
        """
        online = stat_online.fields[0].value.split("/")
        assert online[1] == "20"

    def test_record(self, stat_online):
        """Проверяет правильно ли бот распознает рекорд онлайна.

        Args:
            stat_online: Embed объект ответа.
        """
        assert stat_online.fields[2].value == "33"

    def test_alias_in_footer(self, stat_alias):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи в footer.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert "тест_алиас" in stat_alias.footer.text

    def test_no_pings_for_plot(self, stat_online_as_msg):
        """Проверяет что если пингов недостаточно для построения графика.

        Args:
            stat_online_as_msg: Сообщение ответа.
        """
        assert "слишком мало информации" in stat_online_as_msg.content

    def test_check_yesterday_online(self, get_yest_ping):
        """Проверят правильно ли бот распознает вчерашние пинги.

        Args:
            get_yest_ping: Ответ метода `Statistic.get_yest_ping`.
        """
        assert get_yest_ping == 12

    def test_yest_null(self, get_yest_ping_null):
        """Проверяет правильно ли бот распознает вчерашний онлайн, если записей об этом нету.

        Args:
            get_yest_ping_null: Ответ метода `Statistic.get_yest_ping`.
        """
        assert get_yest_ping_null == "Нету информации"

    def test_plot(self, stat_alias):
        """Проверяет создает ли бот график онлайна.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert stat_alias.image.url == "attachment://127.0.0.5_25565.png"
