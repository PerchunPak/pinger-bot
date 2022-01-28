"""https://docs.pytest.org/en/6.2.x/fixture.html#scope-sharing-fixtures-across-classes-modules-packages-or-session"""
from glob import glob
from os import mkdir, remove, listdir
from shutil import rmtree
from asyncio import get_event_loop
from discord import Intents
from discord.ext.commands import Bot
from discord.ext.test import configure
from pytest import fixture
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.engine.cursor import CursorResult
from src.database import PostgresController


@fixture(scope="session")
async def bot(event_loop):
    """Инициализация бота (и базы данных тоже).

    Args:
        event_loop: Обязательная фикстура для async фикстур.

    Returns:
        Главный объект бота
    """
    print("")  # фиксит логи, лучше не трогать
    bot_intents = Intents.default()
    bot_intents.members = True  # pylint: disable=E0237

    bot_var = Bot(
        command_prefix="",
        description="Пингер бот",
        case_insensitive=False,
        help_command=None,
        intents=bot_intents,
    )
    bot_var.load_extension("tests.commands")
    for file in listdir("./src/commands"):
        if file.endswith(".py") and not file.endswith("_.py"):
            bot_var.load_extension("src.commands." + file[:-3])

    configure(bot_var)

    bot_var.db = PostgresController.get_instance()
    bot_var.app_info = await bot_var.application_info()
    try:
        mkdir("./plots")
    except FileExistsError:
        pass
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


def create_execute(engine):
    """Создает функцию execute

    Args:
        engine: Объект Engine базы данных.

    Returns:
        Функцию execute.
    """

    def execute(to_execute, params: dict = {}, commit: bool = False) -> CursorResult:
        """Выполняет команду(ы) в базу данных.

        Args:
            to_execute: Данные которые отправлять в sqlalchemy.
            params: Параметры передаваемые вместе с запросом.
            commit: Сохранять ли изменения в БД?

        Returns:
            Сырой результат ответа базы данных. Для преобразования в нормальный вид, используйте .one() или .all().
        """
        with engine.connect() as conn:
            result = conn.execute(to_execute, params)
            if commit:
                conn.commit()
        return result

    return execute


@fixture(scope="class")
def database(bot):
    """Очищает базу данных каждый раз.

    Args:
        bot: Главный объект бота.

    Yields:
        Объект дата базы.
    """
    bot.db.drop_tables()
    bot.db.execute = create_execute(bot.db.engine)
    yield bot.db
    bot.db.drop_tables()


def pytest_sessionfinish():
    """Clean up attachment files."""
    files = glob("./dpytest_*.dat")
    for path in files:
        try:
            remove(path)
        except Exception as exception:  # pylint: disable=W0703
            print(f"Error while deleting file {path}: {exception}")
    try:
        rmtree("./plots/")
    except FileNotFoundError:
        pass
