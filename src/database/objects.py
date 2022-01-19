from datetime import datetime, timedelta
from peewee import *
from config import POSTGRES

database = PostgresqlDatabase(POSTGRES)


class Base(Model):
    class Meta:
        database = database


class Servers(Base):
    ip = TextField(unique=true)
    owner = BigIntegerField()
    alias = TextField(null=True, unique=True)
    record = IntegerField(default=0)


class Pings(Base):
    server = ForeignKeyField(Servers)
    players = IntegerField()
    time = DateTimeField(auto_now=True)
