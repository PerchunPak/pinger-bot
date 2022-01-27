"""
Вся работа с дата базой здесь.
"""
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    SmallInteger,
    BigInteger,
    DateTime,
    UniqueConstraint,
    insert,
    update,
    select,
    delete,
)
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.exc import NoResultFound
from config import POSTGRES


class PostgresController:
    """Класс для управления дата базой,
    только тут все взаимодействия с ней.

    Attributes:
        engine: Engine объект дата базы.
        metadata: МетаДата базы данных.
        t: Быстрый доступ к объектам таблиц
    """

    __slots__ = ("engine", "metadata", "t")

    def __init__(self, engine):
        """
        Args:
            engine: Engine объект дата базы.
        """
        self.engine = engine
        self.metadata = MetaData()

    @classmethod
    def get_instance(cls, connect_info: str = POSTGRES):
        """Создает объект класса `PostgresController`.

        Этот метод так же создаст необходимые таблицы.

        Args:
            connect_info: Данные для подключения к дата базе.

        Returns:
            Объект класса.
        """
        engine = create_engine(connect_info, future=True)
        db_obj = cls(engine)
        db_obj.make_tables()
        return db_obj

    def make_tables(self):
        """Создает таблицы в дата базе если их ещё нет."""

        sunpings = Table(
            "sunpings",
            self.metadata,
            Column("ip", String),
            Column("port", SmallInteger),
            Column("time", DateTime),
            Column("players", Integer),
            extend_existing=True,
        )

        sunservers = Table(
            "sunservers",
            self.metadata,
            Column("ip", String),
            Column("port", SmallInteger),
            Column("record", SmallInteger, default=0),
            Column("alias", String, unique=True),
            Column("owner", BigInteger),
            UniqueConstraint("ip", "port"),
            extend_existing=True,
        )

        self.metadata.create_all(self.engine, tables=[sunpings, sunservers])
        self.t.sp = sunpings
        self.t.ss = sunservers

    def execute(self, to_execute, params: dict = {}, commit: bool = False) -> CursorResult:
        """Выполняет команду(ы) в базу данных.

        Args:
            to_execute: Данные которые отправлять в sqlalchemy.
            params: Параметры передаваемые вместе с запросом.
            commit: Сохранять ли изменения в БД?

        Returns:
            Сырой результат ответа базы данных. Для преобразования в нормальный вид, используйте .one() или .all().
        """
        with self.engine.connect() as conn:
            result = conn.execute(to_execute, params)
            if commit:
                conn.commit()
        return result

    def add_server(self, ip: str, port: int, owner_id: int):
        """Добавляет в дата базу новый сервер.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            owner_id: Айди владельца сервера.
        """
        self.execute(insert(self.t.ss).values(ip=ip, port=port, owner=owner_id), commit=True)

    def add_ping(self, ip: str, port: int, players: int):
        """Добавляет данные о пинге в дата базу.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            players: Количество игроков на сервере в момент пинга.
        """
        self.execute(insert(self.t.sp).values(ip=ip, port=port, players=players), commit=True)

    def add_alias(self, alias: str, ip: str, port: int):
        """Добавляет алиас в дата базу.

        Args:
            alias: Новый алиас сервера.
            ip: Айпи сервера.
            port: Порт сервера.
        """
        self.execute(
            update(self.t.ss).values(alias=alias).where(self.t.ss.ip == ip).where(self.t.ss.port == port), commit=True
        )

    def add_record(self, ip: str, port: int, online: int):
        """Добавляет данные о рекорде в дата базу.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.
            online: Рекорд онлайна.
        """
        self.execute(
            update(self.t.ss).values(record=online).where(self.t.ss.ip == ip).where(self.t.ss.port == port), commit=True
        )

    def get_server(self, ip: str, port: int = 25565) -> CursorResult:
        """Возвращает всю информацию сервера.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.

        Returns:
            Объект Result с результатом запроса.
        """
        return self.execute(select(self.t.ss).where(self.t.ss.ip == ip).where(self.t.ss.port == port)).one()

    def get_servers(self) -> CursorResult:
        """Возвращает все сервера.

        Returns:
            Result со всеми серверами.
        """
        return self.execute(select(self.t.ss)).all()

    def get_ip_alias(self, alias: str) -> tuple:
        """Возвращает айпи и порт сервера через алиас.

        Args:
            alias: Алиас который дал юзер.

        Returns:
            Сервер или пустой tuple.
        """
        try:
            result = self.execute(select(self.t.ss).where(self.t.ss == alias)).one()
        except NoResultFound:
            result = ()

        return result

    def get_alias_ip(self, ip: str, port: int) -> tuple:
        """Возвращает алиас сервера через айпи и порт, который дал юзер.

        Args:
            ip: Айпи который дал юзер.
            port: Порт, который дал юзер.

        Returns:
            Сервер или пустой dict.
        """
        try:
            result = self.execute(select(self.t.ss).where(self.t.ss.ip == ip).where(self.t.ss.port == port)).one()
        except NoResultFound:
            result = ()

        return result

    def get_pings(self, ip: str, port: int = 25565) -> list:
        """Возвращает пинги сервера.

        Args:
            ip: Айпи сервера.
            port: Порт сервера.

        Returns:
            Список пингов сервера.
        """
        return self.execute(
            select(self.t.sp).where(self.t.sp.ip == ip).where(self.t.sp.port == port).order_by(self.tt.sp.time)
        ).all()

    def remove_too_old_pings(self):
        """Удаляет пинги старше суток."""
        yesterday = datetime.now() - timedelta(days=1, hours=2)
        self.execute(delete(self.t.sp).where(self.t.sp.time < yesterday))

    def drop_tables(self):
        """Сбрасывает все данные в дата базе."""
        self.metadata.drop_all([self.t.ss, self.t.sp])
        self.make_tables()
