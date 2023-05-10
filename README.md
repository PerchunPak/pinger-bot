# pinger-bot

[![Support Ukraine](https://badgen.net/badge/support/UKRAINE/?color=0057B8&labelColor=FFD700)](https://www.gov.uk/government/news/ukraine-what-you-can-do-to-help)

[![Build Status](https://github.com/PerchunPak/pinger-bot/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/PerchunPak/pinger-bot/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/PerchunPak/pinger-bot/branch/master/graph/badge.svg)](https://codecov.io/gh/PerchunPak/pinger-bot)
[![Documentation Build Status](https://readthedocs.org/projects/pinger-bot/badge/?version=latest)](https://pinger-bot.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python support versions badge](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/)
[![DeepSource](https://deepsource.io/gh/PerchunPak/pinger-bot.svg/?label=active+issues&show_trend=true&token=Tast9YwlUsJbok_-qTQLL0vX)](https://deepsource.io/gh/PerchunPak/pinger-bot/?ref=repository-badge)

Simple discord bot for tracking your Minecraft servers.

- [Документація українською](https://pinger-bot.readthedocs.io/uk_UA/latest)
- [Документация на русском](https://pinger-bot.readthedocs.io/ru/latest)

## Features

- Free! We don't want any money from you!
- Can be self Hosted - the bot is fully under your control!
- You can use it without any hosting!
- Can grab MOTD from any server in one command!
- Supports both Java and Bedrock servers!
- Can be easily localized to your language!

## Try it out!

Check the [invite link](https://discordapp.com/oauth2/authorize?client_id=820582186222616577&permissions=2147485696&scope=bot%20applications.commands)
to invite the bot to your server.

## Screenshots

![/ping](https://github.com/PerchunPak/pinger-bot/blob/master/docs/_static/ping.png?raw=true)

![/alias](https://github.com/PerchunPak/pinger-bot/blob/master/docs/_static/alias.png?raw=true)

![/statistic](https://github.com/PerchunPak/pinger-bot/blob/master/docs/_static/statistic.png?raw=true)

## Installing

```bash
git clone https://github.com/PerchunPak/pinger-bot.git
cd pinger-bot
```

### Installing `poetry`

Next we need install `poetry` with [recommended way](https://python-poetry.org/docs/master/#installation).

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

#### Compiling translations

This requered even if you want just use english.

```bash
pybabel compile -d locales
```

### Database migrations

Those will create database for you. You do not need to create any tables by hand, just run this command:

```bash
alembic -c pinger_bot/migrations/alembic.ini upgrade head
```

### Configuration

All bot configuration happens in `config.yml`, or with enviroment variables.
All configuration settings described in [config.py](https://pinger-bot.readthedocs.io/en/latest/autoapi/pinger_bot/config/).

#### Database

When setting up a database, there are a few additional nuances:

- If you want use SQLite, you need specify path to file. I recomend set absolute path.
- What specify in field `db_uri`? [See this page](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).

### Run the bot

```bash
python pinger_bot
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
pybabel compile -d locales
alembic -c pinger_bot/migrations/alembic.ini upgrade head
```

## Thanks

This project was generated with [python-template](https://github.com/PerchunPak/python-template).
