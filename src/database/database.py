"""
Вся работа с дата базой здесь.
Взято и изменено под свои нужды с https://github.com/dashwav/nano-chan
"""
from src.database.objects import Metods


class PostgresController:
    """Класс для управления дата базой,
    только тут все взаимодействия с ней.

    Attributes:
        pool: Пул дата базы.
    """

    def __init__(self):
        self.pool = Pool()

    @staticmethod
    async def make_tables(): pass

    @staticmethod
    async def __clear_return(): pass

    @classmethod
    async def get_instance(cls):
        """Создает объект класса `PostgresController`.
        Этот метод так же создаст необходимые таблицы.
        Args:
            connect_info: Данные для подключения к дата базе.
        Returns:
            Объект класса.
        """
        return cls()

    async def add_server(self, ip: str, port: int, owner_id: int):
        """Добавляет в дата базу новый сервер.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            owner_id: Айди владельца сервера.
        """
        return Metods.add_server(ip, port, owner_id)

    async def add_ping(self, ip: str, port: int, players: int):
        """Добавляет данные о пинге в дата базу.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            players: Количество игроков на сервере в момент пинга.
        """
        return Metods.add_ping(ip, port, players)

    async def add_alias(self, alias: str, ip: str, port: int):
        """Добавляет алиас в дата базу.

        Args:
            alias: Новый алиас сервера.
            ip: Айпи сервера.
            port: Порт сервера.
        """
        return Metods.add_alias(alias, ip, port)

    async def add_record(self, ip: str, port: int, online: int):
        """Добавляет данные о рекорде в дата базу.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            online: Рекорд онлайна.
        """
        return Metods.add_record(ip, port, online)

    async def get_server(self, ip: str, port: int = 25565) -> dict:
        """Возвращает всю информацию сервера.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.

        Returns:
            Информацию о сервере или пустой dict.
        """
        return Metods.get_server(ip, port)

    async def get_servers(self) -> list:
        """Возвращает все сервера.

        Returns:
            Список со всеми серверами.
        """
        return Metods.get_servers()

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
        return Metods.get_ip_alias(alias)

    async def get_alias_ip(self, ip: str, port: int) -> dict:
        """Возвращает алиас сервера через айпи и порт который дал юзер.

        Args:
            ip: Айпи который дал юзер.
            port: Порт который дал юзер.

        Returns:
            Сервер или пустой dict.
        """
        return Metods.get_alias_ip(ip, port)

    async def get_pings(self, ip: str, port: int = 25565) -> list:
        """Возвращает пинги сервера.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.

        Returns:
            Список пингов сервера.
        """
        return Metods.get_pings(ip, port)

    async def remove_too_old_pings(self):
        """Удаляет пинги старше суток."""
        return Metods.remove_too_old_pings()

    async def drop_tables(self):
        """Сбрасывает все данные в дата базе."""
        return Metods.drop_tables()


class Pool:
    async def execute(self, sql):
        return Metods.get_db_obj().execute_sql(sql)

    async def fetch(self, sql):
        return Metods.get_db_obj().execute_sql(sql)
