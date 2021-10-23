"""
https://docs.pytest.org/en/6.2.x/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session
"""
from glob import glob
from os import remove
from discord import Intents
from discord.ext.commands import Bot
from pytest import fixture
from database import PostgresController
from asyncio import get_event_loop
from discord.ext.test import configure
from shutil import rmtree


@fixture(scope='session')
async def bot(event_loop):
    """Инициализация бота (и базы данных тоже)"""
    print('')  # фиксит логи, лучше не трогать
    bot_intents = Intents.default()
    bot_intents.members = True

    b = Bot(
        command_prefix='',
        description="Пингер бот",
        case_insensitive=False,
        help_command=None,
        intents=bot_intents
    )
    b.load_extension("commands")

    configure(b)

    b.db = await PostgresController.get_instance()
    b.app_info = await b.application_info()
    return b


@fixture(scope="session")
def event_loop():
    """фиксит https://stackoverflow.com/questions/56236637"""
    loop = get_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
def monkeypatch_session(request):
    """фиксит https://github.com/pytest-dev/pytest/issues/363"""
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@fixture(scope='class')
async def database(event_loop, bot):
    """Очищает базу данных каждый раз"""
    await bot.db.drop_tables()
    await bot.db.make_tables()
    yield bot.db
    await bot.db.drop_tables()


def pytest_sessionfinish():
    """Clean up attachment files"""
    files = glob('./dpytest_*.dat')
    for path in files:
        try:
            remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")
    try: rmtree('./plots/')
    except FileNotFoundError: pass
