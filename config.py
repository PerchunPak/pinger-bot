"""Конфиг бота"""

TOKEN = "TOKEN_HERE"
"""Дискорд токен бота"""

POSTGRES = "postgres://pingerbot:password@localhost:5432/pingerbotdb"
"""
Данные от Postgres (СУБД). Это необходимо, чтобы бот мог хранить данные в базе данных SQL.
Данные выглядят так: "postgres://[user]:[password]@[host]:[port]/[database name]" (Некоторые данные не обязательные)
"""
