"""Some configuration fixtures for tests."""
import asyncio
import logging

import _pytest.config
import _pytest.stash
import _pytest.tmpdir as tmpdir
import alembic.command
import alembic.config
import faker.config
import omegaconf
import pytest
import sqlalchemy.ext.asyncio as sqlalchemy_asyncio
import sqlalchemy.orm
import structlog

import pinger_bot.config as config
import pinger_bot.models as models
import tests.custom_fakes as custom_fakes  # we need to import it somewhere
import tests.factories as factories


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
def configure_database(
    tmp_path_factory: tmpdir.TempPathFactory, disable_logging: None, pytestconfig: _pytest.config.Config
) -> None:
    """Configure database, so it will not overwrite production's one. This also requires disabling logging."""
    with omegaconf.open_dict(config.config):  # type: ignore # false-positive because we overwrite type in Config.setup
        config.config.db_uri = pytestconfig.getoption("dburi").format(tempdir=tmp_path_factory.mktemp("database"))

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
    factories.faker.unique._seen = pytestconfig.stash[_faker_unique_key]
    factories.faker.unique._sentinel = _faker_sentinel


@pytest.fixture()  # type: ignore[no-redef] # already defined by an import
def faker(
    faker: faker.Faker, pytestconfig: _pytest.config.Config, _faker_unique_key: _pytest.stash.StashKey[dict], _faker_sentinel: object  # type: ignore[type-arg]
) -> faker.Faker:
    """A part of patch from :func:`.patch_unique_in_factories`."""
    faker.unique._seen = pytestconfig.stash[_faker_unique_key]
    faker.unique._sentinel = _faker_sentinel
    return faker
