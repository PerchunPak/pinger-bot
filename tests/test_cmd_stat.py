"""Тесты для команды "стата"."""
from socket import timeout
from datetime import datetime, timedelta
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed, get_message
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture
from src.commands.statistic import Statistic


class TestStatistic:
    """Класс для тестов и фикстур."""

    @staticmethod
    @fixture(scope="class")
    async def stat_online(event_loop, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        await database.add_server("127.0.0.3", 25565, 0)
        await database.add_record("127.0.0.3", 25565, 33)

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

    @staticmethod
    @fixture(scope="class")
    async def stat_online_as_msg(event_loop, database, monkeypatch_session):
        """Основная фикстура для тестов, отсылает онлайн сервер.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Сообщение ответа.
        """
        await database.add_server("127.0.0.4", 25565, 0)
        await database.add_record("127.0.0.4", 25565, 33)

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

    @staticmethod
    @fixture(scope="class")
    async def stat_alias(event_loop, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Embed объект ответа.
        """
        await database.add_server("127.0.0.5", 25565, 0)
        await database.add_alias("тест_алиас", "127.0.0.5", 25565)
        yesterday = datetime.now() - timedelta(hours=24)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.5", 25565, yesterday, 12)

        # Генерирует 25 пингов
        i = 0
        args = []
        while i <= 25:
            time = datetime.now() - timedelta(minutes=i * 10)
            args.append(("127.0.0.5", 25565, time, i))
            i += 1
        await database.pool.executemany("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", args)

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

    @staticmethod
    @fixture(scope="class")
    async def stat_offline(event_loop, monkeypatch_session):
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

    @staticmethod
    @fixture(scope="class")
    async def get_yest_ping(event_loop, database):
        """Вызывает метод получения вчерашнего пинга.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.

        Returns:
            Ответ метода `Statistic.get_yest_ping`.
        """
        yesterday = datetime.now() - timedelta(hours=24)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.7", 25565, yesterday, 12)

        # Генерирует 25 пингов
        i = 0
        args = []
        while i <= 25:
            time = datetime.now() - timedelta(minutes=i * 10)
            args.append(("127.0.0.7", 25565, time, i))
            i += 1
        await database.pool.executemany("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", args)

        pings = await database.get_pings("127.0.0.7", 25565)
        return await Statistic.get_yest_ping(pings)

    @staticmethod
    @fixture(scope="class")
    async def get_yest_ping_null(event_loop, database):
        """Вызывает метод получения вчерашнего пинга.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект дата базы.

        Returns:
            Ответ метода `Statistic.get_yest_ping`.
        """
        pings = await database.get_pings("127.0.0.8", 25565)
        return await Statistic.get_yest_ping(pings)

    @staticmethod
    def test_color(stat_online):
        """Проверят цвет в ответе бота.

        Args:
            stat_online: Embed объект ответа.
        """
        assert str(stat_online.color) == str(Color.green())

    @staticmethod
    def test_alias_in(stat_alias):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert "тест_алиас" in stat_alias.title

    @staticmethod
    def test_alias_numip(stat_alias):
        """Проверят правильно ли бот распознает цифровое айпи, если использовать алиас.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert "127.0.0.5:25565" in stat_alias.description

    @staticmethod
    def test_online_in_description(stat_online):
        """Проверят правильно ли бот пишет онлайн сервера.

        Args:
            stat_online: Embed объект ответа.
        """
        assert "**Онлайн**" in stat_online.description

    @staticmethod
    def test_offline_in_description(stat_offline):
        """Проверят правильно ли бот пишет офлайн сервера.

        Args:
            stat_offline: Embed объект ответа.
        """
        assert "**Офлайн**" in stat_offline.description

    @staticmethod
    def test_thumbnail_link(stat_alias):
        """Проверяет ссылку в маленькой картинке справо сверху.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert stat_alias.thumbnail.url == "https://api.mcsrvstat.us/icon/127.0.0.5:25565"

    @staticmethod
    def test_online(stat_online):
        """Проверяет правильно ли бот распознает текущий онлайн.

        Args:
            stat_online: Embed объект ответа.
        """
        online = stat_online.fields[0].value.split("/")
        assert online[0] == "5"

    @staticmethod
    def test_online_max(stat_online):
        """Проверяет правильно ли бот распознает максимальный онлайн.

        Args:
            stat_online: Embed объект ответа.
        """
        online = stat_online.fields[0].value.split("/")
        assert online[1] == "20"

    @staticmethod
    def test_record(stat_online):
        """Проверяет правильно ли бот распознает рекорд онлайна.

        Args:
            stat_online: Embed объект ответа.
        """
        assert stat_online.fields[2].value == "33"

    @staticmethod
    def test_alias_in_footer(stat_alias):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи в footer.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert "тест_алиас" in stat_alias.footer.text

    @staticmethod
    def test_no_pings_for_plot(stat_online_as_msg):
        """Проверяет что если пингов не достаточно для построения графика.

        Args:
            stat_online_as_msg: Сообщение ответа.
        """
        assert "слишком мало информации" in stat_online_as_msg.content

    @staticmethod
    def test_check_yesterday_online(get_yest_ping):
        """Проверят правильно ли бот распознает вчерашние пинги.

        Args:
            get_yest_ping: Ответ метода `Statistic.get_yest_ping`.
        """
        assert get_yest_ping == 12

    @staticmethod
    def test_yest_null(get_yest_ping_null):
        """Проверяет правильно ли бот распознает вчерашний онлайн, если записей об этом нету.

        Args:
            get_yest_ping_null: Ответ метода `Statistic.get_yest_ping`.
        """
        assert get_yest_ping_null == "Нету информации"

    @staticmethod
    def test_plot(stat_alias):
        """Проверяет создает ли бот график онлайна.

        Args:
            stat_alias: Embed объект ответа.
        """
        assert stat_alias.image.url == "attachment://127.0.0.5_25565.png"
