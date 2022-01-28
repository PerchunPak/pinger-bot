"""Файл для теста дата базы."""
from datetime import datetime, timedelta
from pytest import fixture
from src.database import PostgresController


@fixture(scope="session")
async def database(event_loop):
    """Инициализирует дата базу.

    Args:
        event_loop: Обязательная фикстура для async фикстур.

    Yields:
        Объект дата базы.
    """  # FIXME db.pool
    db = PostgresController.get_instance()
    db.pool.execute("DROP TABLE IF EXISTS sunpings;")
    db.pool.execute("DROP TABLE IF EXISTS sunservers;")
    yield db
    db.pool.execute("DROP TABLE IF EXISTS sunpings;")
    db.pool.execute("DROP TABLE IF EXISTS sunservers;")


class TestAddFunctions:
    """Класс для тестов add_* методов."""

    async def test_add_server(self, database):
        """Проверяет метод add_server.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.11", 25565, 0)
        server = database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.11' AND port=25565")  # FIXME db.pool
        assert len(server) > 0

    async def test_add_server_owner_id(self, database):
        """Проверяет метод add_server, правильно ли записывает owner_id.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.12", 25565, 123123)
        server = database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.12' AND port=25565")  # FIXME db.pool
        assert server[0]["owner"] == 123123

    async def test_add_ping(self, database):
        """Проверяет метод add_ping.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_ping("127.0.0.13", 25565, 33)
        ping = database.pool.fetch("SELECT * FROM sunpings WHERE ip='127.0.0.13' AND port=25565")  # FIXME db.pool
        assert ping[0]["players"] == 33

    async def test_add_alias(self, database):
        """Проверяет метод add_alias.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.14", 25565, 0)
        database.add_alias("тест", "127.0.0.14", 25565)
        server = database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.14' AND port=25565")  # FIXME db.pool
        assert server[0]["alias"] == "тест"

    async def test_add_record(self, database):
        """Проверяет метод add_record.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.15", 25565, 0)
        database.add_record("127.0.0.15", 25565, 33)
        server = database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.15' AND port=25565")  # FIXME db.pool
        assert server[0]["record"] == 33


class TestGetFunctions:
    """Класс для тестов get_* методов."""

    async def test_get_server(self, database):
        """Проверяет метод get_server.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.16", 25565, 0)
        answer = database.get_server("127.0.0.16", 25565)
        right_answer = database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.16' AND port=25565")  # FIXME db.pool
        assert answer == dict(right_answer[0])

    async def test_get_servers(self, database):
        """Проверяет метод get_servers.

        Args:
            database: Объект дата базы.
        """
        database.pool.execute("DROP TABLE IF EXISTS sunpings;")  # FIXME db.pool
        database.pool.execute("DROP TABLE IF EXISTS sunservers;")  # FIXME db.pool
        database.make_tables()
        database.add_server("127.0.0.17", 25565, 0)
        database.add_server("127.0.0.18", 25565, 0)
        database.add_server("127.0.0.19", 25565, 0)
        answer = database.get_servers()
        right_answer = database.pool.fetch("SELECT * FROM sunservers;")  # FIXME db.pool
        assert answer == right_answer

    async def test_get_servers_len(self, database):
        """Проверяет метод get_servers_len.

        Args:
            database: Объект дата базы.
        """
        database.pool.execute("DROP TABLE IF EXISTS sunpings;")  # FIXME db.pool
        database.pool.execute("DROP TABLE IF EXISTS sunservers;")  # FIXME db.pool
        database.make_tables()
        database.add_server("127.0.0.20", 25565, 0)
        database.add_server("127.0.0.21", 25565, 0)
        database.add_server("127.0.0.22", 25565, 0)
        answer = database.get_servers()
        assert len(answer) == 3

    async def test_get_ip_alias(self, database):
        """Проверяет метод get_ip_alias.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.23", 25565, 0)
        database.add_alias("тест123", "127.0.0.23", 25565)
        answer = database.get_ip_alias("тест123")
        right_answer = database.pool.fetch("SELECT ip, port FROM sunservers WHERE alias='тест123';")  # FIXME db.pool
        assert answer == dict(right_answer[0])

    async def test_get_pings(self, database):
        """Проверяет метод get_pings.

        Args:
            database: Объект дата базы.
        """
        database.pool.execute("DROP TABLE IF EXISTS sunpings;")  # FIXME db.pool
        database.pool.execute("DROP TABLE IF EXISTS sunservers;")  # FIXME db.pool
        database.make_tables()
        database.add_ping("127.0.0.24", 25565, 1)
        database.add_ping("127.0.0.24", 25565, 2)
        database.add_ping("127.0.0.24", 25565, 3)
        answer = database.get_pings("127.0.0.24", 25565)
        right_answer = database.pool.fetch("SELECT * FROM sunpings WHERE ip='127.0.0.24' AND port=25565;")  # FIXME db.pool
        assert answer == right_answer

    async def test_get_pings_len(self, database):
        """Проверяет метод get_pings_len.

        Args:
            database: Объект дата базы.
        """
        database.pool.execute("DROP TABLE IF EXISTS sunpings;")  # FIXME db.pool
        database.pool.execute("DROP TABLE IF EXISTS sunservers;")  # FIXME db.pool
        database.make_tables()
        database.add_ping("127.0.0.25", 25565, 1)
        database.add_ping("127.0.0.25", 25565, 2)
        database.add_ping("127.0.0.25", 25565, 3)
        answer = database.get_pings("127.0.0.25", 25565)
        assert len(answer) == 3


class TestAnotherFunctions:
    """Класс для тестов других методов."""

    async def test_clear_return(self, database):
        """Проверяет метод __clear_return

        Иначе сделать никак, сделайте PL если знаете
        как это лучше сделать.

        Args:
            database: Объект дата базы.
        """
        database.add_ping("test_server", 25566, 123)
        right_answer = database.pool.fetch("SELECT * FROM sunpings")  # FIXME db.pool
        right_answer = right_answer[0]
        answer = database._PostgresController__clear_return([right_answer])
        assert dict(right_answer) == answer

    async def test_clear_return_empty(self, database):
        """Проверяет метод __clear_return пустым ответом.

        Args:
            database: Объект дата базы.
        """
        returned = database._PostgresController__clear_return([])
        assert {} == returned

    async def test_make_tables(self, database):
        """Проверяет метод make_tables.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.pool.execute("SELECT * FROM sunpings;")  # FIXME db.pool
        database.pool.execute("SELECT * FROM sunservers;")  # FIXME db.pool

    async def test_remove_too_old_pings(self, database):
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
        database.pool.execute(
            "INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_1h, 1
        )  # FIXME db.pool
        database.pool.execute(
            "INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_12h, 2
        )  # FIXME db.pool
        database.pool.execute(
            "INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_23h, 3
        )  # FIXME db.pool
        database.pool.execute(
            "INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_1d, 4
        )  # FIXME db.pool
        database.pool.execute(
            "INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_3d, 5
        )  # FIXME db.pool
        database.remove_too_old_pings()
        sql = """
            SELECT * FROM sunpings
            WHERE ip=$1 AND port=$2
            ORDER BY time;
        """
        pings = database.pool.fetch(sql, "127.0.0.26", 25565)  # FIXME db.pool
        pings_right = [
            ("127.0.0.26", 25565, time_1d, 4),
            ("127.0.0.26", 25565, time_23h, 3),
            ("127.0.0.26", 25565, time_12h, 2),
            ("127.0.0.26", 25565, time_1h, 1),
        ]
        i = 0
        for ping in pings:
            assert tuple(ping) == pings_right[i]
            i += 1

    async def test_drop_table_sunpings(self, database):
        """Проверяет метод drop_tables на таблице sunpings.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_ping("127.0.0.27", 25565, 333)
        database.drop_tables()
        sunpings = database.pool.fetch("SELECT * FROM sunpings;")  # FIXME db.pool
        assert len(sunpings) == 0

    async def test_drop_table_sunservers(self, database):
        """Проверяет метод drop_tables на таблице sunservers.

        Args:
            database: Объект дата базы.
        """
        database.make_tables()
        database.add_server("127.0.0.28", 25565, 0)
        database.drop_tables()
        sunservers = database.pool.fetch("SELECT * FROM sunservers;")  # FIXME db.pool
        assert len(sunservers) == 0
