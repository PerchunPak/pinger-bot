"""Module for the one test, because pytest is not collecting tests from ``conftest.py``."""
import importlib
import pathlib

import pytest
import pytest_mock

import pinger_bot.config as config

IGNORED_MODULES = {config.BASE_DIR / "pinger_bot" / "ext" / "scheduling.py"}


@pytest.mark.parametrize("path", set((config.BASE_DIR / "pinger_bot" / "ext").rglob("[!_]*.py")) - IGNORED_MODULES)
def test_load_method(mocker: pytest_mock.MockerFixture, path: pathlib.Path) -> None:
    """Recursive looks for the extensions, and test their load method."""
    module = importlib.import_module(".".join(path.relative_to(config.BASE_DIR).parts)[:-3])

    assert "load" in dir(module), "Extensions must have a `load` method."
    stub = mocker.stub()
    stub.add_plugin = mocker.stub()
    module.load(stub)

    stub.add_plugin.assert_called()
