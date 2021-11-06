"""
Тесты для команды "стата"
"""
from socket import timeout
from datetime import datetime, timedelta
from time import sleep
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture, mark


class TestStatistic:
    """Класс для тестов и фикстур"""

    @staticmethod
    @fixture(scope='class')
    async def stat_online_not_added(event_loop, bot, database, monkeypatch_session):
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

    @staticmethod
    @fixture(scope='class')
    async def stat_online(event_loop, bot, database, monkeypatch_session):
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

    @staticmethod
    @fixture(scope='class')
    async def stat_alias(event_loop, bot, database, monkeypatch_session):
        """Фикстура для тестов поддерживает ли команда алиасы"""
        await database.add_server('127.0.0.5', 0, 25565)
        await database.add_alias('тест_алиас', '127.0.0.5', 25565)
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

    @staticmethod
    @fixture(scope='class')
    async def stat_not_valid(event_loop, bot, database, monkeypatch_session):
        """Вызывает команду с не валидным айпи"""
        monkeypatch_session.undo()
        await message("стата www")
        embed = get_embed()
        while str(embed.color) == str(Color.orange()):  # ждет пока бот не отошлет результаты вместо
            sleep(0.01)                                 # "ожидайте, в процессе"
            embed = get_embed()

        return embed

    @staticmethod
    @fixture(scope='class')
    async def stat_offline(event_loop, bot, database, monkeypatch_session):
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

    @staticmethod
    @mark.asyncio
    async def test_server_not_added_color(event_loop, bot, database, stat_online_not_added):
        """Проверят цвет в ответе бота, если сервер не добавлен"""
        await database.make_tables()
        assert str(stat_online_not_added.color) == str(Color.red())

    @staticmethod
    def test_online(bot, database, stat_online):
        """Проверяет правильно ли бот распознает текущий онлайн"""
        online = stat_online.fields[0].value.split('/')
        assert online[0] == '5'

    @staticmethod
    def test_online_max(bot, database, stat_online):
        """Проверяет правильно ли бот распознает максимальный онлайн"""
        online = stat_online.fields[0].value.split('/')
        assert online[1] == '20'

    @staticmethod
    def test_record(bot, database, stat_online):
        """Проверяет правильно ли бот распознает рекорд онлайна"""
        assert stat_online.fields[2].value == '33'

    @staticmethod
    def test_online_yest_null(bot, database, stat_online):
        """Проверяет правильно ли бот распознает вчерашний онлайн, если записей об этом нету"""
        assert stat_online.fields[1].value == 'Нету информации'

    @staticmethod
    def test_color(bot, database, stat_online):
        """Проверят цвет в ответе бота"""
        assert str(stat_online.color) == str(Color.green())

    @staticmethod
    def test_alias_color(bot, stat_alias, database):
        """Проверят цвет в ответе бота, если использовать алиас"""
        assert str(stat_alias.color) == str(Color.green())

    @staticmethod
    def test_alias_numip(bot, stat_alias, database):
        """Проверят правильно ли бот распознает цифровое айпи, если использовать алиас"""
        assert '127.0.0.5' in stat_alias.description
        assert '25565' in stat_alias.description

    @staticmethod
    def test_alias_in(bot, stat_alias, database):
        """Проверяет правильно ли бот распознает алиас, и не выводит цифровой айпи"""
        assert 'тест_алиас' in stat_alias.title

    @staticmethod
    def test_plot(bot, stat_alias, database):
        """Проверяет создает ли бот график онлайна"""
        assert stat_alias.image.url == 'attachment://127.0.0.5_25565.png'

    @staticmethod
    def test_check_yesterday_online(bot, stat_alias, database):
        """Проверят правильно ли бот распознает вчерашние пинги"""
        assert stat_alias.fields[1].value == '12'

    @staticmethod
    def test_ip_not_valid(bot, database, stat_not_valid):
        """Проверят цвет в ответе бота, если айпи не валидный"""
        assert str(stat_not_valid.color) == str(Color.red())

    @staticmethod
    def test_offline_color(bot, database, stat_offline):
        """Проверяет цвет Embed-а когда сервер оффлайн"""
        assert str(stat_offline.color) == str(Color.red())
