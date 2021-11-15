"""Файл для теста дата базы."""
from datetime import datetime, timedelta
from pytest import fixture, mark
from src.database import PostgresController


@fixture(scope='session')
async def database(event_loop):
    """Инициализирует дата базу.

    Args:
        event_loop: Обязательная фикстура для async фикстур.

    Yields:
        Объект дата базы.
    """
    db = await PostgresController.get_instance()
    await db.pool.execute("DROP TABLE IF EXISTS sunpings;")
    await db.pool.execute("DROP TABLE IF EXISTS sunservers;")
    yield db
    await db.pool.execute("DROP TABLE IF EXISTS sunpings;")
    await db.pool.execute("DROP TABLE IF EXISTS sunservers;")


class TestAddFunctions:
    """Класс для тестов add_* функций."""
    @staticmethod
    @mark.asyncio
    async def test_add_server(database):
        """Проверяет функцию add_server.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.11', 25565, 0)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.11' AND port=25565")
        assert len(server) > 0

    @staticmethod
    @mark.asyncio
    async def test_add_server_owner_id(database):
        """Проверяет функцию add_server, правильно ли записывает owner_id.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.12', 25565, 123123)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.12' AND port=25565")
        assert server[0]['owner'] == 123123

    @staticmethod
    @mark.asyncio
    async def test_add_ping(database):
        """Проверяет функцию add_ping.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_ping('127.0.0.13', 25565, 33)
        ping = await database.pool.fetch("SELECT * FROM sunpings WHERE ip='127.0.0.13' AND port=25565")
        assert ping[0]['players'] == 33

    @staticmethod
    @mark.asyncio
    async def test_add_alias(database):
        """Проверяет функцию add_alias.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.14', 25565, 0)
        await database.add_alias('тест', '127.0.0.14', 25565)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.14' AND port=25565")
        assert server[0]['alias'] == 'тест'

    @staticmethod
    @mark.asyncio
    async def test_add_record(database):
        """Проверяет функцию add_record.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.15', 25565, 0)
        await database.add_record('127.0.0.15', 25565, 33)
        server = await database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.15' AND port=25565")
        assert server[0]['record'] == 33


class TestGetFunctions:
    """Класс для тестов get_* функций."""
    @staticmethod
    @mark.asyncio
    async def test_get_server(database):
        """Проверяет функцию get_server.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.16', 25565, 0)
        answer = await database.get_server('127.0.0.16', 25565)
        right_answer = await database.pool.fetch("SELECT * FROM sunservers WHERE ip='127.0.0.16' AND port=25565")
        assert answer == dict(right_answer[0])

    @staticmethod
    @mark.asyncio
    async def test_get_servers(database):
        """Проверяет функцию get_servers.

        Args:
            database: Объект дата базы.
        """
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_server('127.0.0.17', 25565, 0)
        await database.add_server('127.0.0.18', 25565, 0)
        await database.add_server('127.0.0.19', 25565, 0)
        answer = await database.get_servers()
        right_answer = await database.pool.fetch("SELECT * FROM sunservers;")
        assert answer == right_answer

    @staticmethod
    @mark.asyncio
    async def test_get_servers_len(database):
        """Проверяет функцию get_servers_len.

        Args:
            database: Объект дата базы.
        """
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_server('127.0.0.20', 25565, 0)
        await database.add_server('127.0.0.21', 25565, 0)
        await database.add_server('127.0.0.22', 25565, 0)
        answer = await database.get_servers()
        assert len(answer) == 3

    @staticmethod
    @mark.asyncio
    async def test_get_ip_alias(database):
        """Проверяет функцию get_ip_alias.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.23', 25565, 0)
        await database.add_alias('тест123', '127.0.0.23', 25565)
        answer = await database.get_ip_alias('тест123')
        right_answer = await database.pool.fetch("SELECT ip, port FROM sunservers WHERE alias='тест123';")
        assert answer == dict(right_answer[0])

    @staticmethod
    @mark.asyncio
    async def test_get_pings(database):
        """Проверяет функцию get_pings.

        Args:
            database: Объект дата базы.
        """
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_ping('127.0.0.24', 25565, 1)
        await database.add_ping('127.0.0.24', 25565, 2)
        await database.add_ping('127.0.0.24', 25565, 3)
        answer = await database.get_pings('127.0.0.24', 25565)
        right_answer = await database.pool.fetch("SELECT * FROM sunpings WHERE ip='127.0.0.24' AND port=25565;")
        assert answer == right_answer

    @staticmethod
    @mark.asyncio
    async def test_get_pings_len(database):
        """Проверяет функцию get_pings_len.

        Args:
            database: Объект дата базы.
        """
        await database.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await database.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await database.make_tables()
        await database.add_ping('127.0.0.25', 25565, 1)
        await database.add_ping('127.0.0.25', 25565, 2)
        await database.add_ping('127.0.0.25', 25565, 3)
        answer = await database.get_pings('127.0.0.25', 25565)
        assert len(answer) == 3


class TestAnotherFunctions:
    """Класс для тестов других функций."""
    @staticmethod
    @mark.asyncio
    async def test_make_tables(database):
        """Проверяет функцию make_tables.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.pool.execute("SELECT * FROM sunpings;")
        await database.pool.execute("SELECT * FROM sunservers;")

    @staticmethod
    @mark.asyncio
    async def test_remove_too_old_pings(database):
        """Проверяет функцию remove_too_old_pings.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        time_1h = datetime.now() - timedelta(hours=1)
        time_12h = datetime.now() - timedelta(hours=12)
        time_23h = datetime.now() - timedelta(hours=23)
        time_1d = datetime.now() - timedelta(days=1, minutes=10)
        time_3d = datetime.now() - timedelta(days=3)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_1h, 1)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_12h, 2)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_23h, 3)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_1d, 4)
        await database.pool.execute("INSERT INTO sunpings VALUES ($1, $2, $3, $4);", "127.0.0.26", 25565, time_3d, 5)
        await database.remove_too_old_pings()
        sql = """
            SELECT * FROM sunpings
            WHERE ip=$1 AND port=$2
            ORDER BY time;
        """
        pings = await database.pool.fetch(sql, "127.0.0.26", 25565)
        pings_right = [('127.0.0.26', 25565, time_23h, 3),
                       ('127.0.0.26', 25565, time_12h, 2),
                       ('127.0.0.26', 25565, time_1h, 1)]
        i = 0
        for ping in pings:
            assert tuple(ping) == pings_right[i]
            i += 1

    @staticmethod
    @mark.asyncio
    async def test_drop_table_sunpings(database):
        """Проверяет функцию drop_tables на таблице sunpings.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_ping('127.0.0.27', 25565, 333)
        await database.drop_tables()
        sunpings = await database.pool.fetch("SELECT * FROM sunpings;")
        assert len(sunpings) == 0

    @staticmethod
    @mark.asyncio
    async def test_drop_table_sunservers(database):
        """Проверяет функцию drop_tables на таблице sunservers.

        Args:
            database: Объект дата базы.
        """
        await database.make_tables()
        await database.add_server('127.0.0.28', 25565, 0)
        await database.drop_tables()
        sunservers = await database.pool.fetch("SELECT * FROM sunservers;")
        assert len(sunservers) == 0
