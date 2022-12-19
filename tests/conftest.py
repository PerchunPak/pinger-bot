"""Some configuration fixtures for tests."""
import asyncio
import logging
import typing

import _pytest.config
import _pytest.stash
import alembic.command
import alembic.config
import faker
import omegaconf
import pytest
import sqlalchemy
import structlog
from _pytest import tmpdir
from sqlalchemy.ext import asyncio as sqlalchemy_asyncio

from pinger_bot import config, models
from tests import (
    custom_fakes,  # we need to import it somewhere # skipcq: PY-W2000 # nopycln: import
)
from tests import factories


@pytest.fixture(scope="session")
def event_loop():
    """Set event loop to session scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def disable_logging() -> None:
    """Disable logging."""
    structlog.configure(
        processors=[structlog.testing.LogCapture()], wrapper_class=structlog.make_filtering_bound_logger(logging.ERROR)
    )


def pytest_addoption(parser):
    """Allow change the DB for tests.

    .. note:: You should use ``{tempdir}`` instead of ``:memory:``, because in second variant, migrations can't work.
    """
    parser.addoption("--dburi", action="store", default="sqlite+aiosqlite:///{tempdir}/db.sqlite3")


@pytest.fixture(scope="session", autouse=True)
def patch_config(tmp_path_factory: tmpdir.TempPathFactory, pytestconfig: _pytest.config.Config) -> None:
    """Patch the config, to work with tests."""
    with omegaconf.open_dict(config.config):  # type: ignore # false-positive because we overwrite type in Config.setup
        config.config.discord_token = "some random string"  # don't use faker because of scope mismatch
        config.config.db_uri = pytestconfig.getoption("dburi").format(tempdir=tmp_path_factory.mktemp("database"))


async def _clear_db(session: sqlalchemy_asyncio.AsyncSession) -> None:
    await session.execute(sqlalchemy.delete(models.Ping))
    await session.execute(sqlalchemy.delete(models.Server))
    await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def clear_db(patch_config: None, configure_database: None) -> typing.AsyncIterator[None]:
    """Clear database from all information."""
    async with models.db.session() as session:
        await _clear_db(session)
        yield
        await _clear_db(session)


@pytest.fixture(scope="session", autouse=True)
def configure_database(disable_logging: None, patch_config: None) -> None:
    """Configure database, so it will not overwrite production's one.

    This also requires disabling logging and patching the config.
    """
    alembic_cfg = alembic.config.Config("pinger_bot/migrations/alembic.ini")
    alembic_cfg.set_section_option("logger_alembic", "level", "ERROR")
    alembic.command.upgrade(alembic_cfg, "head")

    models.db = models.Database()


@pytest.fixture(scope="session")
def _faker_unique_key(pytestconfig: _pytest.config.Config) -> _pytest.stash.StashKey[dict]:  # type: ignore[type-arg]
    """A key for a variable, which storing unique faker objects.

    This function also creates variable inside stash.
    """
    key = _pytest.stash.StashKey[dict]()  # type: ignore[type-arg] # we don't care about content
    pytestconfig.stash[key] = {}
    return key


@pytest.fixture(scope="session")
def _faker_sentinel() -> object:
    """Sentinel for faker."""
    return object()


@pytest.fixture(scope="session", autouse=True)
def patch_unique_in_factories(
    pytestconfig: _pytest.config.Config, _faker_unique_key: _pytest.stash.StashKey[dict], _faker_sentinel: object  # type: ignore[type-arg]
) -> None:
    """Patch the unique in factories, so they will be shared across all tests."""
    factories.faker.unique._seen = pytestconfig.stash[_faker_unique_key]  # skipcq: PYL-W0212 # private attribute
    factories.faker.unique._sentinel = _faker_sentinel  # skipcq: PYL-W0212 # private attribute


@pytest.fixture()  # type: ignore[no-redef] # already defined by an import
def faker(
    faker: faker.Faker, pytestconfig: _pytest.config.Config, _faker_unique_key: _pytest.stash.StashKey[dict], _faker_sentinel: object  # type: ignore[type-arg]
) -> faker.Faker:
    """A part of patch from :func:`.patch_unique_in_factories`."""
    faker.unique._seen = pytestconfig.stash[_faker_unique_key]  # skipcq: PYL-W0212 # private attribute
    faker.unique._sentinel = _faker_sentinel  # skipcq: PYL-W0212 # private attribute
    return faker
