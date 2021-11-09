"""
https://docs.pytest.org/en/6.2.x/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session
"""
from glob import glob
from os import remove, listdir
from shutil import rmtree
from asyncio import get_event_loop
from discord import Intents
from discord.ext.commands import Bot
from discord.ext.test import configure
from pytest import fixture
from src.database import PostgresController
from _pytest.monkeypatch import MonkeyPatch


@fixture(scope='session')
async def bot(event_loop):
    """Инициализация бота (и базы данных тоже)"""
    print('')  # фиксит логи, лучше не трогать
    bot_intents = Intents.default()
    bot_intents.members = True  # pylint: disable=E0237

    bot_var = Bot(
        command_prefix='',
        description="Пингер бот",
        case_insensitive=False,
        help_command=None,
        intents=bot_intents
    )
    bot_var.load_extension("tests.commands")
    for file in listdir("./src/commands"):
        if file.endswith(".py") and not file.startswith("_"):
            bot_var.load_extension("src.commands." + file[:-3])

    configure(bot_var)

    bot_var.db = await PostgresController.get_instance()
    bot_var.app_info = await bot_var.application_info()
    return bot_var


@fixture(scope="session")
def event_loop():
    """фиксит https://stackoverflow.com/questions/56236637"""
    loop = get_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
def monkeypatch_session(request):
    """фиксит https://github.com/pytest-dev/pytest/issues/363"""
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
        except Exception as exception:  # pylint: disable=W0703
            print(f"Error while deleting file {path}: {exception}")
    try: rmtree('./plots/')
    except FileNotFoundError: pass