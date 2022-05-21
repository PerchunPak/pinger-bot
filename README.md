# pinger-bot

[![Build Status](https://github.com/PerchunPak/pinger-bot/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/PerchunPak/pinger-bot/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/PerchunPak/pinger-bot/branch/master/graph/badge.svg)](https://codecov.io/gh/PerchunPak/pinger-bot)
[![Documentation Build Status](https://readthedocs.org/projects/pinger-bot/badge/?version=latest)](https://pinger-bot.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python support versions badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/downloads/)

Простой бот для отслеживания статуса и статистики своих MineCraft серверов.

## Особенности

- Бесплатно! Мы не попросим ни копейки за использование!
- SelfHosted - Вы сами управляете ботом от начала и до конца!

## Установка

```bash
git clone https://github.com/PerchunPak/pinger-bot.git
cd pinger-bot
```

Затем установите `poetry` [рекомендованым путем](https://python-poetry.org/docs/master/#installation).

Если вы на платформе Linux, используйте команду:

```bash
curl -sSL https://install.python-poetry.org | python -
```

Если вы на Windows, откройте PowerShell от имени администратора и используйте:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

И наконец установим зависимости:

```bash
poetry install
```

Так же для работы бота необходимо указать какую СУБД вы будете использовать.
На данный момент мы поддерживаем только `SQLite`, `MySQL` и `PostgreSQL`.
Для установки необходимой зависимости, необходимо просто использовать аргумент `-E` с названием СУБД в нижнем регистре.

Например:

```bash
poetry install -E mysql
```

После установки зависимостей, нужно скомпилировать файлы перевода.
```bash
poetry run pybabel compile -d locales
```

И после этого, нужно применить миграции:
```bash
poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head
```

Так же нужно настроить конфигурацию бота, [смотрите этот раздел](#конфигурация).

Ну и наконец, запустить бота:
```bash
poetry run python pinger_bot/pinger_bot.py
```

Если вам все еще что-то не понятно - вы всегда можете написать мне!

## Конфигурация

Вся настройка бота происходит в файле `.env` или `settings.ini`. Все настройки описаны в файле [config.py](/pinger_bot/config.py).

### База данных

При настройке базы данных есть несколько дополнительных нюансов:

- Если вы используете SQLite, вам нужно указать путь к базе данных. Рекомендуется указывать абсолютный путь.
- Чтобы узнать что указывать в поле `DB_URI`, [смотрите эту статью](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).

## Обновление

Для обновления бота, просто скачайте заново репозиторий (предварительно сохранив конфиги и базу данных), или если вы
использовали `git` для установки запустите команду `git pull`.

После чего, нужно обновить переводы и базу данных, шаги аналогичны установке бота.

```bash
poetry run pybabel compile -d locales
poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head
```

## Спасибо

Этот проект был сгенерирован с помощью [`fire-square-style`](https://github.com/fire-square/fire-square-style).
Текущая версия примера: [c94d4ab18b51f38443ab456eea8aa0553faf43d8](https://github.com/fire-square/fire-square-style/tree/c94d4ab18b51f38443ab456eea8aa0553faf43d8).
Смотрите что [обновилось](https://github.com/fire-square/fire-square-style/compare/c94d4ab18b51f38443ab456eea8aa0553faf43d8...master) с того времени.
