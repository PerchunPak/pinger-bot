"""Тесты для общих методов из файла /src/commands/commands_.py."""
from socket import timeout
from discord import Color
from discord.ext.test import message, get_embed
from mcstatus import MinecraftServer
from mcstatus.pinger import PingResponse
from pytest import fixture, mark
from src.objects import ServerInfo
from src.commands.commands_ import MetodsForCommands

# TODO Добавить тесты для последних изменений


class TestMetodsForCommands:
    """Класс для тестов и фикстур."""
    @staticmethod
    @fixture(scope="session")
    def metods_for_commands(bot):
        """Фикстура сохраняющая экземпляр класса.

        Args:
            bot: Главный объект бота.

        Returns:
            Экземпляр класса `MetodsForCommands`.
        """
        return MetodsForCommands(bot)

    @staticmethod
    @fixture(scope="class")
    async def wait_please():
        """Фикстура получающая ответ от тестовой команды wait_please.

        Returns:
            Embed объект ответа.
        """
        await message("wait_please example.com")
        return get_embed()

    @staticmethod
    @fixture(scope="class")
    async def fail_message_online():
        """Фикстура получающая ответ от тестовой команды fail_message.

        Returns:
            Embed объект ответа.
        """
        await message("fail_message example.com 1")
        return get_embed()

    @staticmethod
    @fixture(scope="class")
    async def fail_message_offline():
        """Фикстура получающая ответ от тестовой команды fail_message, но теперь если online=False.

        Returns:
            Embed объект ответа.
        """
        await message("fail_message example.com 0")
        return get_embed()

    @staticmethod
    @mark.asyncio
    async def test_parse_ip_alias(database, metods_for_commands):
        """Тест на проверку алиаса в методе MetodsForCommands.parse_ip.

        Args:
            database: Объект дата базы.
            metods_for_commands: Экземпляр класса `MetodsForCommands`.
        """
        await database.pool.execute("INSERT INTO sunservers (ip, port, owner) VALUES ($1, 25565, 0);", "127.0.0.29")
        await database.pool.execute("UPDATE sunservers SET alias = $2 "
                                    "WHERE ip = $1 AND port = 25565;", "127.0.0.29", "тест28")
        dns_info = MinecraftServer("127.0.0.29")
        answer = await metods_for_commands.parse_ip("тест28")
        assert answer == ServerInfo(True, "тест28", dns_info, "127.0.0.29", "25565")

    @staticmethod
    @mark.asyncio
    async def test_parse_ip_valid(metods_for_commands):
        """Тест на проверку действий при валидном айпи.

        Args:
            metods_for_commands: Экземпляр класса `MetodsForCommands`.
        """
        dns_info = MinecraftServer("127.0.0.30")
        answer = await metods_for_commands.parse_ip("127.0.0.30")
        assert answer == ServerInfo(True, None, dns_info, "127.0.0.30", "25565")

    @staticmethod
    @mark.asyncio
    async def test_parse_ip_not_valid(metods_for_commands):
        """Тест на проверку действий при не валидном айпи.

        Args:
            metods_for_commands: Экземпляр класса `MetodsForCommands`.
        """
        dns_info = MinecraftServer("www")
        answer = await metods_for_commands.parse_ip("www")
        assert answer == ServerInfo(False, None, dns_info, None, "25565")

    @staticmethod
    def compare_ping_response_objects(obj1: PingResponse, obj2: PingResponse) -> bool:
        """Метод сравнивает объекты PingResponse.

        Args:
            obj1: Первый объект для сравнивания.
            obj2: Второй объект для сравнивания.

        Returns:
            Результат сравнения.
        """
        ret = [
            obj1.raw == obj2.raw,
            obj1.players.__dict__ == obj2.players.__dict__,
            obj1.version.__dict__ == obj2.version.__dict__,
            obj1.description == obj2.description,
            obj1.favicon == obj2.favicon
        ]

        return False not in ret

    @mark.asyncio
    async def test_ping_server_valid(self, metods_for_commands, monkeypatch_session):
        """Тест на проверку действий при валидном айпи в методе MetodsForCommands.ping_server.

        Args:
            metods_for_commands: Экземпляр класса `MetodsForCommands`.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.
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

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        expected_dns_info = MinecraftServer.lookup("127.0.0.31")
        status, info = await metods_for_commands.ping_server("127.0.0.31")
        # __dict__ чтобы можно было сравнивать классы
        # без этого при сравнении оно всегда выдает False
        assert self.compare_ping_response_objects(status, fake_server_answer()) and \
               info.dns.__dict__ == expected_dns_info.__dict__ and \
               info.__dict__ == ServerInfo(True, None, info.dns, "127.0.0.31", "25565").__dict__

    @staticmethod
    @mark.asyncio
    async def test_ping_server_not_valid(metods_for_commands):
        """Тест на проверку действий при не валидном айпи.

        Args:
            metods_for_commands: Экземпляр класса `MetodsForCommands`.
        """
        dns_info = MinecraftServer("www")
        answer = await metods_for_commands.ping_server("www")
        assert answer == (False, ServerInfo(False, None, dns_info, None, "25565"))

    @staticmethod
    @mark.asyncio
    async def test_ping_server_not_answer(metods_for_commands, monkeypatch_session):
        """Тест на проверку действий если сервер не ответил.

        Args:
            metods_for_commands: Экземпляр класса `MetodsForCommands`.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.
        """
        def fake_server_answer(class_self=None):
            """Когда сервер выключен, модуль вызывает exception socket.timeout.

            Args:
                class_self: Иногда при вызове функции, так же приходит аргумент `self`.

            Raises:
                Фейковый ответ сервера (то есть негативный).
            """
            raise timeout

        monkeypatch_session.setattr(MinecraftServer, "status", fake_server_answer)
        expected_dns_info = MinecraftServer.lookup("127.0.0.32")
        status, info = await metods_for_commands.ping_server("127.0.0.32")
        # __dict__ чтобы можно было сравнивать классы
        # без этого при сравнении оно всегда выдает False
        assert status is False and \
               info.dns.__dict__ == expected_dns_info.__dict__ and \
               info.__dict__ == ServerInfo(True, None, info.dns, "127.0.0.32", "25565").__dict__

    @staticmethod
    def test_wait_please_color(wait_please):
        """Тест на проверку цвета в сообщении wait_please.

        Args:
            wait_please: Embed объект ответа.
        """
        assert str(wait_please.color) == str(Color.orange())

    @staticmethod
    def test_wait_please_ip_in_title(wait_please):
        """Тест на проверку есть ли айпи в title.

        Args:
            wait_please: Embed объект ответа.
        """
        assert "example.com" in wait_please.title

    @staticmethod
    def test_fail_message_online_color(fail_message_online):
        """Тест на проверку цвета в сообщении fail_message (online).

        Args:
            fail_message_online: Embed объект ответа.
        """
        assert str(fail_message_online.color) == str(Color.red())

    @staticmethod
    def test_fail_message_online_ip_in_title(fail_message_online):
        """Тест на проверку есть ли айпи в title.

        Args:
            fail_message_online: Embed объект ответа.
        """
        assert "example.com" in fail_message_online.title

    @staticmethod
    def test_fail_message_online_status(fail_message_online):
        """Тест на проверку правильного статуса в описании Embed'а.

        Args:
            fail_message_online: Embed объект ответа.
        """
        assert "Онлайн" in fail_message_online.description

    @staticmethod
    def test_fail_message_offline_color(fail_message_offline):
        """Тест на проверку цвета в сообщении fail_message (offline).

        Args:
            fail_message_offline: Embed объект ответа.
        """
        assert str(fail_message_offline.color) == str(Color.red())

    @staticmethod
    def test_fail_message_offline_ip_in_title(fail_message_offline):
        """Тест на проверку есть ли айпи в title.

        Args:
            fail_message_offline: Embed объект ответа.
        """
        assert "example.com" in fail_message_offline.title

    @staticmethod
    def test_fail_message_offline_status(fail_message_offline):
        """Тест на проверку правильного статуса в описании Embed'а.

        Args:
            fail_message_offline: Embed объект ответа.
        """
        assert "Офлайн" in fail_message_offline.description
