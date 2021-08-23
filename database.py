"""
Вся работа с дата базой здесь.
Взято и изменено под свои нужды с https://github.com/dashwav/nano-chan
"""
from time import localtime
from datetime import time
from typing import Optional
from asyncpg import Record, create_pool
from asyncpg.pool import Pool

from config import POSTGRES


def parse_record(record: Record) -> Optional[tuple]:
    """
    Parse a asyncpg Record object to a tuple of values
    :param record: theasyncpg Record object
    :return: the tuple of values if it's not None, else None

    P.S. я не знаю что это делает, но похоже
         что то важное, лучше оставлю
    """
    try:
        return tuple(record.values())
    except AttributeError:
        return None


async def make_tables(pool: Pool):
    """
    Создает таблицы в дата базе если их ещё нет.
    :param pool: пул для подключения.
    """

    sunpings = """
    CREATE TABLE IF NOT EXISTS sunpings (
        ip CIDR NOT NULL,
        port SMALLINT NOT NULL DEFAULT 25565,
        time TIME NOT NULL,
        players INTEGER NOT NULL
    );
    """

    sunservers = """
    CREATE TABLE IF NOT EXISTS sunservers (
        numip CIDR NOT NULL,
        port SMALLINT NOT NULL DEFAULT 25565,
        record SMALLINT NOT NULL DEFAULT 0,
        alias TEXT,
        owner BIGSERIAL NOT NULL,
        UNIQUE (numip, port)
    );
    """

    db_entries = (sunpings, sunservers)
    for db_entry in db_entries:
        await pool.execute(db_entry)


class PostgresController:  # TODO обновить коментарии
    """
    Мы будем использовать 'sunpinger' схему для дата базы
    Откуда она берется, никто не знает
    """
    __slots__ = 'pool'

    def __init__(self, pool: Pool):
        self.pool = pool

    @classmethod
    async def get_instance(cls, connect_kwargs: str = POSTGRES, pool: Pool = None):
        """
        (лучше английский чем гугл переводчик)
        Get a new instance of `PostgresController`
        This method will create the appropriate tables needed.
        :param connect_kwargs:
            Keyword arguments for the
            :func:`asyncpg.connection.connect` function.
        :param pool: an existing connection pool.
        One of `pool` or `connect_kwargs` must not be None.
        :return: a new instance of `PostgresController`
        """
        assert connect_kwargs or pool, (
            'Предоставьте либо пул подключений, либо данные о '
            'подключении для создания нового пула подключений.'
        )
        if not pool:
            pool = await create_pool(connect_kwargs)
        await make_tables(pool)
        return cls(pool)

    async def add_server(self, numip: str, ownerId: str, port: int = 25565):
        """
        Добавляет в дата базу новый сервер
        :param numip: цифровое айпи IPv4 сервера
        :param ownerId: айди владельца сервера
        :param port: порт сервера (необязательный аргумент)
        """
        sql = """
        INSERT INTO sunservers (numip, port, owner) VALUES ($1, $2, $3);
        """

        await self.pool.execute(sql, numip, port, ownerId)

    async def add_ping(self, ip: str, port: int, players: int):
        """
        Добавляет данные о пинге в дата базу
        :param ip: цифровое айпи IPv4 сервера
        :param port: порт сервера
        :param players: количество игроков на сервере в момент пинга
        """
        tmF = localtime()
        tm = time(tmF[3], tmF[4])
        sql = """
        INSERT INTO sunpings VALUES ($1, $2, $3, $4)
        """
        await self.pool.execute(sql, ip, port, tm, players)

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
        Добавляет данные о пинге в дата базу
        :param alias: новый алиас сервера
        :param ip: цифровое айпи IPv4 сервера
        :param port: порт сервера
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
        WHERE ip=$1 AND port=$2;
        """
        return await self.pool.fetch(sql, numip, port)

    async def get_ping_yest(self, numip: str, port: int = 25565):
        """
        Возвращает пинг сервера сутки назад через FETCH
        """
        tmF = localtime()
        tm = time(tmF[3], tmF[4])
        sql = """
        SELECT players FROM sunpings
        WHERE ip=$1 AND port=$2 AND time=$3;
        """
        return await self.pool.fetch(sql, numip, port, tm)
