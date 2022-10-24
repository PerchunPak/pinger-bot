# pinger-bot

[![Support Ukraine](https://badgen.net/badge/support/UKRAINE/?color=0057B8&labelColor=FFD700)](https://www.gov.uk/government/news/ukraine-what-you-can-do-to-help)

[![Build Status](https://github.com/PerchunPak/pinger-bot/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/PerchunPak/pinger-bot/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/PerchunPak/pinger-bot/branch/master/graph/badge.svg)](https://codecov.io/gh/PerchunPak/pinger-bot)
[![Documentation Build Status](https://readthedocs.org/projects/pinger-bot/badge/?version=latest)](https://pinger-bot.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python support versions badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/downloads/)

Simple discord bot for tracking your MineCraft servers.

- [Документація українською](https://pinger-bot.readthedocs.io/uk_UA/latest)
- [Документация на русском](https://pinger-bot.readthedocs.io/ru/latest)

## Features

- Free! We don't want any money from you!
- Self Hosted - Bot fully under your control!

## Installing

```bash
git clone https://github.com/PerchunPak/pinger-bot.git
cd pinger-bot
```

### Installing `poetry`

Next we need install `poetry` with [recomended way](https://python-poetry.org/docs/master/#installation).

If you use Linux, use command:

```bash
curl -sSL https://install.python-poetry.org | python -
```

If you use Windows, open PowerShell with admin privilages and use:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Installing dependencies

```bash
poetry install --only main
```

Also, for bot working, you need specify which database you will use.
For now, we only support `SQLite`, `MySQL` and `PostgreSQL`.
For installing required dependence, we need just use argument `-E` with lower-cased database name.

Example:

```bash
poetry install --only main -E mysql
```

### Compiling translations

This requered even if you want just use english.

```bash
poetry run pybabel compile -d locales
```

### Database migrations

Those will create database for you. You do not need to create any tables by hand, just run this command:

```bash
poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head
```

### Configuration

All bot configuration happends in `config.yml`, or with enviroment variables.
All configuration settings described in [config.py](https://pinger-bot.readthedocs.io/en/latest/autoapi/pinger_bot/config/).

#### Database

When setting up a database, there are a few additional nuances:

- If you want use SQLite, you need specify path to file. I recomend set absolute path.
- What specify in field `db_uri`? [See this page](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).

### Run the bot

```bash
poetry run python pinger_bot
```

### If something is not clear

You can always write me!

## Using in Docker

See [docs](https://pinger-bot.readthedocs.io/en/latest/pages/docker/).

## Updating

For updating, just redownload repository (do not forget save config and database),
if you used `git` for donwloading, just run `git pull`.

After that, you need update translations and database, commands the same as in installing section:

```bash
poetry run pybabel compile -d locales
poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head
```

## Thanks

This project was generated with [fire-square-style](https://github.com/fire-square/fire-square-style).
Current template version: [624a5259df6a2ba4fa9629f491e2966d030e496b](https://github.com/fire-square/fire-square-style/tree/624a5259df6a2ba4fa9629f491e2966d030e496b).
See what [updated](https://github.com/fire-square/fire-square-style/compare/624a5259df6a2ba4fa9629f491e2966d030e496b...master).
