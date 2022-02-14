"""Файл для теста дата базы."""
from datetime import datetime, timedelta
from pytest import fixture
from sqlalchemy import select, insert
from tests.conftest import create_execute
from src.database import DatabaseController


@fixture(scope="session")
def database():
    """Инициализирует дата базу.

    Yields:
        Объект дата базы.
    """
    db = DatabaseController.get_instance(connect_info="sqlite:///:memory:")
    db.execute = create_execute(db.engine)
    db.drop_tables()
    yield db
    db.drop_tables()


class TestAddFunctions:
    """Класс для тестов add_* методов."""

    def test_add_server(self, database):
        """Проверяет метод add_server.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.11", 25565, 0)
        server = database.execute(
            select(database.t.ss).where(database.t.ss.c.ip == "127.0.0.11").where(database.t.ss.c.port == 25565)
        ).one()
        assert len(server) > 0

    def test_add_server_owner_id(self, database):
        """Проверяет метод add_server, правильно ли записывает owner_id.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.12", 25565, 123123)
        server = database.execute(
            select(database.t.ss).where(database.t.ss.c.ip == "127.0.0.12").where(database.t.ss.c.port == 25565)
        ).one()
        assert server["owner"] == 123123

    def test_add_ping(self, database):
        """Проверяет метод add_ping.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_ping("127.0.0.13", 25565, 33)
        ping = database.execute(
            select(database.t.sp).where(database.t.sp.c.ip == "127.0.0.13").where(database.t.sp.c.port == 25565)
        ).one()
        assert ping["players"] == 33

    def test_add_alias(self, database):
        """Проверяет метод add_alias.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.14", 25565, 0)
        database.add_alias("тест", "127.0.0.14", 25565)
        server = database.execute(
            select(database.t.ss).where(database.t.ss.c.ip == "127.0.0.14").where(database.t.ss.c.port == 25565)
        ).one()
        assert server["alias"] == "тест"

    def test_add_record(self, database):
        """Проверяет метод add_record.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.15", 25565, 0)
        database.add_record("127.0.0.15", 25565, 33)
        server = database.execute(
            select(database.t.ss).where(database.t.ss.c.ip == "127.0.0.15").where(database.t.ss.c.port == 25565)
        ).one()
        assert server["record"] == 33


class TestGetFunctions:
    """Класс для тестов get_* методов."""

    def test_get_server(self, database):
        """Проверяет метод get_server.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.16", 25565, 0)
        answer = database.get_server("127.0.0.16", 25565)
        right_answer = database.execute(
            select(database.t.ss).where(database.t.ss.c.ip == "127.0.0.16").where(database.t.ss.c.port == 25565)
        ).one()
        assert answer == right_answer

    def test_get_servers(self, database):
        """Проверяет метод get_servers.

        Args:
            database: Объект дата базы.
        """
        database.drop_tables()
        database.add_server("127.0.0.17", 25565, 0)
        database.add_server("127.0.0.18", 25565, 0)
        database.add_server("127.0.0.19", 25565, 0)
        answer = database.get_servers()
        right_answer = database.execute(select(database.t.ss)).all()
        assert answer == right_answer

    def test_get_servers_len(self, database):
        """Проверяет метод get_servers_len.

        Args:
            database: Объект дата базы.
        """
        database.drop_tables()
        database.add_server("127.0.0.20", 25565, 0)
        database.add_server("127.0.0.21", 25565, 0)
        database.add_server("127.0.0.22", 25565, 0)
        answer = database.get_servers()
        assert len(answer) == 3

    def test_get_ip_alias(self, database):
        """Проверяет метод get_ip_alias.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.23", 25565, 0)
        database.add_alias("тест123", "127.0.0.23", 25565)
        answer = database.get_ip_alias("тест123")
        right_answer = database.execute(select(database.t.ss).where(database.t.ss.c.alias == "тест123")).one()
        assert answer == right_answer

    def test_get_pings(self, database):
        """Проверяет метод get_pings.

        Args:
            database: Объект дата базы.
        """
        database.drop_tables()
        database.add_ping("127.0.0.24", 25565, 1)
        database.add_ping("127.0.0.24", 25565, 2)
        database.add_ping("127.0.0.24", 25565, 3)
        answer = database.get_pings("127.0.0.24", 25565)
        right_answer = database.execute(
            select(database.t.sp).where(database.t.sp.c.ip == "127.0.0.24").where(database.t.sp.c.port == 25565)
        ).all()
        assert answer == right_answer

    def test_get_pings_len(self, database):
        """Проверяет метод get_pings_len.

        Args:
            database: Объект дата базы.
        """
        database.drop_tables()
        database.add_ping("127.0.0.25", 25565, 1)
        database.add_ping("127.0.0.25", 25565, 2)
        database.add_ping("127.0.0.25", 25565, 3)
        answer = database.get_pings("127.0.0.25", 25565)
        assert len(answer) == 3

    def test_get_alias_ip(self, database):
        """Проверяет метод get_alias_ip.

        Args:
            database: Объект дата базы.
        """
        database.drop_tables()
        database.add_server("example.org", 25565, 0)
        database.add_alias("example", "example.org", 25565)
        answer = database.get_alias_ip("example.org", 25565)
        right_answer = database.execute(
            select(database.t.ss.c.alias).where(database.t.ss.c.ip == "example.org").where(database.t.ss.c.port == 25565)
        ).one()["alias"]
        assert answer == right_answer


class TestAnotherFunctions:
    """Класс для тестов других методов."""

    def test_make_tables(self, database):
        """Проверяет метод make_tables.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.execute(select(database.t.sp))
        database.execute(select(database.t.ss))

    def test_remove_too_old_pings(self, database):
        """Проверяет метод remove_too_old_pings.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        time_1h = datetime.now() - timedelta(hours=1)
        time_12h = datetime.now() - timedelta(hours=12)
        time_23h = datetime.now() - timedelta(hours=23)
        time_1d = datetime.now() - timedelta(days=1, minutes=10)
        time_3d = datetime.now() - timedelta(days=3)
        database.execute(insert(database.t.sp).values(ip="127.0.0.26", port=25565, time=time_1h, players=1))
        database.execute(insert(database.t.sp).values(ip="127.0.0.26", port=25565, time=time_12h, players=2))
        database.execute(insert(database.t.sp).values(ip="127.0.0.26", port=25565, time=time_23h, players=3))
        database.execute(insert(database.t.sp).values(ip="127.0.0.26", port=25565, time=time_1d, players=4))
        database.execute(insert(database.t.sp).values(ip="127.0.0.26", port=25565, time=time_3d, players=5))
        database.remove_too_old_pings()
        pings = database.execute(
            select(database.t.sp).where(database.t.sp.c.ip == "127.0.0.26").where(database.t.sp.c.port == 25565)
        ).all()
        pings_right = [
            {"127.0.0.26", 25565, time_1d, 4},
            {"127.0.0.26", 25565, time_23h, 3},
            {"127.0.0.26", 25565, time_12h, 2},
            {"127.0.0.26", 25565, time_1h, 1},
        ]
        i = 0
        for ping in pings:
            assert ping == pings_right[i]
            i += 1

    def test_drop_table_sunpings(self, database):
        """Проверяет метод drop_tables на таблице sunpings.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_ping("127.0.0.27", 25565, 333)
        database.drop_tables()
        sunpings = database.execute(select(database.t.sp)).all()
        assert len(sunpings) == 0

    def test_drop_table_sunservers(self, database):
        """Проверяет метод drop_tables на таблице sunservers.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.28", 25565, 0)
        database.drop_tables()
        sunservers = database.execute(select(database.t.ss)).all()
        assert len(sunservers) == 0
