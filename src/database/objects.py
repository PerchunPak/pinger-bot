from datetime import datetime, timedelta
from peewee import PostgresqlDatabase, Model, TextField, IntegerField, \
    SmallIntegerField, DateTimeField, BigIntegerField, ForeignKeyField
from config import POSTGRES

database = PostgresqlDatabase(POSTGRES)


class UnknownField(object):
    def __init__(self, *_, **__): pass


class Base(Model):
    class Meta:
        database = database


class SunServers(Base):
    ip = TextField()
    port = SmallIntegerField()
    owner = BigIntegerField()
    alias = TextField(null=True, unique=True)
    record = SmallIntegerField(default=0)

    class Meta:
        # поля ip и port должны быть уникальными
        indexes = (
            (('ip', 'port'), True),
        )


class SunPings(Base):
    server = ForeignKeyField(SunServers)
    players = IntegerField()
    time = DateTimeField()


class Metods:
    @staticmethod
    def add_server(ip, port, owner):
        SunServers.create(ip=ip, port=port, owner=owner)

    @staticmethod
    def add_ping(ip: str, port: int, players: int):
        server = SunServers.select() \
            .where((SunServers.ip == ip) & (SunServers.port == port))
        SunPings.create(server=server, players=players, time=datetime.now())

    @staticmethod
    def add_alias(alias: str, ip: str, port: int):
        SunServers.update({SunServers.alias: alias}) \
            .where((SunServers.ip == ip) & (SunServers.port == port))

    @staticmethod
    def add_record(ip: str, port: int, online: int):
        SunServers.update({SunServers.record: online}) \
            .where((SunServers.ip == ip) & (SunServers.port == port))

    @staticmethod
    def get_server(ip: str, port: int):
        return SunServers.select() \
            .where((SunServers.ip == ip) & (SunServers.port == port))

    @staticmethod
    def get_servers():
        return SunServers.select()

    @staticmethod
    def get_ip_alias(alias: str):
        return SunServers.select(SunServers.ip, SunServers.port) \
            .where(SunServers.alias == alias)

    @staticmethod
    def get_alias_ip(ip: str, port: int):
        return SunServers.select(SunServers.alias) \
            .where((SunServers.ip == ip) & (SunServers.port == port))

    @staticmethod
    def get_pings(ip: str, port: int):
        return SunPings.select() \
            .where((SunPings.ip == ip) & (SunPings.port == port)) \
            .order_by(SunPings.time)

    @staticmethod
    def get_db_obj():
        return database

    @staticmethod
    def remove_too_old_pings():
        yesterday = datetime.now() - timedelta(days=1, hours=2)
        SunPings.delete() \
            .where(SunPings.time < yesterday)

    @staticmethod
    def drop_tables():
        SunServers.drop_table()
        SunPings.drop_table()

        SunServers.create_table()
        SunPings.create_table()
