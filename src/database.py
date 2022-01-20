"""
Вся работа с дата базой здесь.
Взято и изменено под свои нужды с https://github.com/dashwav/nano-chan
"""
from datetime import datetime, timedelta
from asyncpg import create_pool
from asyncpg.pool import Pool
from config import POSTGRES


class PostgresController:
    """Класс для управления дата базой,
    только тут все взаимодействия с ней.

    Attributes:
        pool: Пул дата базы.
    """

    __slots__ = ("pool",)

    def __init__(self, pool: Pool):
        """
        Args:
            pool: Пул дата базы.
        """
        self.pool = pool

    @classmethod
    async def get_instance(cls, connect_info: str = POSTGRES):
        """Создает объект класса `PostgresController`.

        Этот метод так же создаст необходимые таблицы.

        Args:
            connect_info: Данные для подключения к дата базе.

        Returns:
            Объект класса.
        """
        pool = await create_pool(connect_info)
        pg_controller = cls(pool)
        await pg_controller.make_tables()
        return pg_controller

    async def make_tables(self):
        """Создает таблицы в дата базе если их ещё нет."""

        sunpings = """
        CREATE TABLE IF NOT EXISTS sunpings (
            ip TEXT NOT NULL,
            port SMALLINT NOT NULL DEFAULT 25565,
            time TIMESTAMP,
            players INTEGER NOT NULL
        );
        """

        sunservers = """
        CREATE TABLE IF NOT EXISTS sunservers (
            ip TEXT NOT NULL,
            port SMALLINT NOT NULL DEFAULT 25565,
            record SMALLINT NOT NULL DEFAULT 0,
            alias TEXT UNIQUE,
            owner BIGSERIAL NOT NULL,
            UNIQUE (ip, port)
        );
        """

        db_entries = (sunpings, sunservers)
        for db_entry in db_entries:
            await self.pool.execute(db_entry)

    @staticmethod
    async def __clear_return(result: list):
        """Что бы не было копипаста, этот метод
        возвращает чистый ответ.

        Args:
            result: Результат метода который нужно вернуть.

        Returns:
            Чистый ответ метода/функции.
        """
        if len(result) != 0:
            return dict(result[0])
        else:
            return {}

    async def add_server(self, ip: str, port: int, owner_id: int):
        """Добавляет в дата базу новый сервер.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            owner_id: Айди владельца сервера.
        """
        sql = """
        INSERT INTO sunservers (ip, port, owner) VALUES ($1, $2, $3);
        """

        await self.pool.execute(sql, ip, port, owner_id)

    async def add_ping(self, ip: str, port: int, players: int):
        """Добавляет данные о пинге в дата базу.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            players: Количество игроков на сервере в момент пинга.
        """
        sql = """
        INSERT INTO sunpings VALUES ($1, $2, $3, $4)
        """
        await self.pool.execute(sql, ip, port, datetime.now(), players)

    async def add_alias(self, alias: str, ip: str, port: int):
        """Добавляет алиас в дата базу.

        Args:
            alias: Новый алиас сервера.
            ip: Айпи сервера.
            port: Порт сервера.
        """
        sql = """
        UPDATE sunservers
        SET alias = $1
        WHERE ip = $2 AND port = $3;
        """
        await self.pool.execute(sql, alias, ip, port)

    async def add_record(self, ip: str, port: int, online: int):
        """Добавляет данные о рекорде в дата базу.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            online: Рекорд онлайна.
        """
        sql = """
        UPDATE sunservers
        SET record = $1
        WHERE ip = $2 AND port = $3;
        """
        await self.pool.execute(sql, online, ip, port)

    async def get_server(self, ip: str, port: int = 25565) -> dict:
        """Возвращает всю информацию сервера.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.

        Returns:
            Информацию о сервере или пустой dict.
        """
        sql = """
        SELECT * FROM sunservers
        WHERE ip=$1 AND port=$2;
        """
        result = await self.pool.fetch(sql, ip, port)
        return await self.__clear_return(result)

    async def get_servers(self) -> list:
        """Возвращает все сервера.

        Returns:
            Список со всеми серверами.
        """
        return await self.pool.fetch("SELECT * FROM sunservers;")

    async def get_ip_alias(self, alias: str) -> dict:
        """Возвращает айпи и порт сервера через алиас.

        Args:
            alias: Алиас который дал юзер.

        Returns:
            Сервер или пустой dict.
        """
        sql = """
        SELECT ip, port FROM sunservers
        WHERE alias=$1;
        """
        result = await self.pool.fetch(sql, alias)
        return await self.__clear_return(result)

    async def get_alias_ip(self, ip: str, port: int) -> dict:
        """Возвращает алиас сервера через айпи и порт который дал юзер.

        Args:
            ip: Айпи который дал юзер.
            port: Порт который дал юзер.

        Returns:
            Сервер или пустой dict.
        """
        sql = """
        SELECT alias FROM sunservers
        WHERE ip=$1 AND port=$2;
        """
        result = await self.pool.fetch(sql, ip, port)
        return await self.__clear_return(result)

    async def get_pings(self, ip: str, port: int = 25565) -> list:
        """Возвращает пинги сервера.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.

        Returns:
            Список пингов сервера.
        """
        sql = """
        SELECT * FROM sunpings
        WHERE ip=$1 AND port=$2
        ORDER BY time;
        """
        return await self.pool.fetch(sql, ip, port)

    async def remove_too_old_pings(self):
        """Удаляет пинги старше суток."""
        yesterday = datetime.now() - timedelta(days=1, hours=2)
        sql = """
        DELETE FROM sunpings
        WHERE time < $1
        """
        return await self.pool.execute(sql, yesterday)

    async def drop_tables(self):
        """Сбрасывает все данные в дата базе."""
        await self.pool.execute("DROP TABLE IF EXISTS sunpings;")
        await self.pool.execute("DROP TABLE IF EXISTS sunservers;")
        await self.make_tables()
