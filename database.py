"""
Вся работа с дата базой здесь.
Взято и изменено под свои нужды с https://github.com/dashwav/nano-chan
"""
from datetime import datetime, timedelta
from asyncpg import create_pool
from asyncpg.pool import Pool
from config import POSTGRES


class PostgresController:
    """
    Класс для управления датабазой,
    только тут все взаимодействия с ней
    """
    __slots__ = 'pool'

    def __init__(self, pool: Pool):
        self.pool = pool

    @classmethod
    async def get_instance(cls, connect_kwargs: str = POSTGRES, pool: Pool = None):
        """
        Создает обьект класса `PostgresController`
        Этот метод создаст необходимые таблицы
        :param connect_kwargs:
            Аргументы для
            :func:`asyncpg.connection.connect` функции
        :param pool: существующий пул подключений
        `pool` или `connect_kwargs` должны быть None
        :return: новый обьект класса `PostgresController`
        """
        assert connect_kwargs or pool, (
            'Предоставьте либо пул подключений, либо данные о '
            'подключении для создания нового пула подключений.'
        )
        if not pool:
            pool = await create_pool(connect_kwargs)
        return cls(pool)

    async def make_tables(self):
        """
        Создает таблицы в дата базе если их ещё нет.
        """

        sunpings = """
        CREATE TABLE IF NOT EXISTS sunpings (
            ip CIDR NOT NULL,
            port SMALLINT NOT NULL DEFAULT 25565,
            time TIMESTAMP,
            players INTEGER NOT NULL
        );
        """

        # айпи может менятся в зависимости от домена
        # TODO перенести хранение айпи в str
        sunservers = """
        CREATE TABLE IF NOT EXISTS sunservers (
            numip CIDR NOT NULL,
            port SMALLINT NOT NULL DEFAULT 25565,
            record SMALLINT NOT NULL DEFAULT 0,
            alias TEXT UNIQUE,
            owner BIGSERIAL NOT NULL,
            UNIQUE (numip, port)
        );
        """

        db_entries = (sunpings, sunservers)
        for db_entry in db_entries:
            await self.pool.execute(db_entry)

    async def add_server(self, numip: str, owner_id: int, port: int = 25565):
        """
        Добавляет в дата базу новый сервер
        :param numip: цифровое айпи IPv4 сервера
        :param owner_id: айди владельца сервера
        :param port: порт сервера (необязательный аргумент)
        """
        sql = """
        INSERT INTO sunservers (numip, port, owner) VALUES ($1, $2, $3);
        """

        await self.pool.execute(sql, numip, port, owner_id)

    async def add_ping(self, ip: str, port: int, players: int):
        """
        Добавляет данные о пинге в дата базу
        :param ip: цифровое айпи IPv4 сервера
        :param port: порт сервера
        :param players: количество игроков на сервере в момент пинга
        """
        sql = """
        INSERT INTO sunpings VALUES ($1, $2, $3, $4)
        """
        await self.pool.execute(sql, ip, port, datetime.now(), players)

    async def add_alias(self, alias: str, ip: str, port: int):
        """
        Добавляет данные о пинге в дата базу
        :param alias: новый алиас сервера
        :param ip: цифровое айпи IPv4 сервера
        :param port: порт сервера
        """
        sql = """
        UPDATE sunservers
        SET alias = $1
        WHERE numip = $2 AND port = $3;
        """
        await self.pool.execute(sql, alias, ip, port)

    async def add_record(self, numip: str, port: int = 25565, online: int = 0):
        """
        Добавляет данные о рекорде в дата базу
        :param numip: цифровое айпи IPv4 сервера
        :param port: порт сервера
        :param online: рекорд онлайна
        """
        sql = """
        UPDATE sunservers
        SET record = $1
        WHERE numip = $2 AND port = $3;
        """
        await self.pool.execute(sql, online, numip, port)

    async def get_server(self, numip: str, port: int = 25565):
        """
        Возвращает всю информацию сервера
        """
        sql = """
        SELECT * FROM sunservers
        WHERE numip=$1 AND port=$2;
        """
        return await self.pool.fetch(sql, numip, port)

    async def get_servers(self):
        """
        Возвращает все сервера
        """
        sql = """
        SELECT * FROM sunservers;
        """
        return await self.pool.fetch(sql)

    async def get_ip_alias(self, alias: str):
        """
        Возвращает айпи и порт сервера через алиас
        """
        sql = """
        SELECT numip, port FROM sunservers
        WHERE alias=$1;
        """
        return await self.pool.fetch(sql, alias)

    async def get_pings(self, numip: str, port: int = 25565):
        """
        Возвращает пинги сервера
        """
        sql = """
        SELECT * FROM sunpings
        WHERE ip=$1 AND port=$2
        ORDER BY time;
        """
        return await self.pool.fetch(sql, numip, port)

    async def remove_too_old_pings(self):
        """
        Удаляет пинги старше суток
        """
        yesterday = datetime.now() - timedelta(days=1)
        sql = """
        DELETE FROM sunpings
        WHERE time < $1
        """
        return await self.pool.execute(sql, yesterday)

    async def drop_tables(self):
        """
        Сбрасывает все данные в датабазе
        """
        return (
            await self.pool.execute("DROP TABLE IF EXISTS sunpings;"),
            await self.pool.execute("DROP TABLE IF EXISTS sunservers;"),
            await self.make_tables()
        )
