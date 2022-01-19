"""Конфиг бота."""
from os import environ


TOKEN = environ.get("PINGERBOT_DISCORD_TOKEN", "-->TOKEN_HERE<--")
"""Дискорд токен бота."""

POSTGRES = environ.get(
    "PINGERBOT_POSTGRES", "postgres://[user]:[password]@[host]:[port]/[database name]"
)
"""
Данные от Postgres (СУБД). Это необходимо, чтобы бот мог хранить данные в базе данных SQL.
Данные выглядят так: "postgres://[user]:[password]@[host]:[port]/[database name]" (Некоторые данные не обязательные).

ВАЖНО: Если вы планируете использовать дата базу запущеную через докер, укажите вместо [host] значение db.
"""
