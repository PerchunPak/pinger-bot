"""Some tests for the :mod:`pinger_bot.bot` module."""
import logging
import typing
from unittest import mock

import faker as faker_package
import omegaconf
import pytest
import pytest_mock

from pinger_bot import bot, config


class TestPingerBot:
    """Tests for the class :class:`pinger_bot.bot.PingerBot`."""

    def test_init_passing_kwargs_to_bot_app(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Test that the :func:`pinger_bot.bot.PingerBot.__init__` function passes kwargs to the \
        :func:`lightbulb.BotApp.__init__`."""
        mocked = mocker.patch("lightbulb.BotApp.__init__")
        kwargs = faker.pydict()
        kwargs.pop("event", None)  # see https://github.com/hynek/structlog/issues/372

        bot.PingerBot(**kwargs)

        mocked.assert_called_once()
        for expected in kwargs.items():
            assert expected in mocked.call_args.kwargs.items()

    def test_run_called_required_methods(self, mocker: pytest_mock.MockerFixture) -> None:
        """Test that the :func:`pinger_bot.bot.PingerBot.run` function calls the required methods."""
        mocked: typing.List[mock.MagicMock] = []
        for to_patch in [
            "pinger_bot.bot.PingerBot.handle_debug_options",
            "pinger_bot.bot.PingerBot.__init__",
            "pinger_bot.bot.PingerBot.load_extensions_from",
            "lightbulb.BotApp.run",
        ]:
            mocked.append(mocker.patch(to_patch, return_value=None))

        bot.PingerBot.run()

        for mocked_method in mocked:
            mocked_method.assert_called_once()

    @pytest.mark.parametrize("verbose", (True, False))
    @pytest.mark.parametrize("debug", (True, False))
    def test_logging_set_correct_values(self, mocker: pytest_mock.MockerFixture, verbose: bool, debug: bool) -> None:
        """Test that the :func:`pinger_bot.bot.PingerBot.handle_debug_options` function set the correct values."""
        with omegaconf.open_dict(
            config.config  # type: ignore[arg-type] # false-positive because we overwrite type in Config.setup
        ):
            config.config.verbose, config.config.debug = verbose, debug
        mocked_configure_level = mocker.patch("structlog.make_filtering_bound_logger")

        bot.PingerBot.handle_debug_options()

        assert logging.root.level == (logging.DEBUG if debug else logging.WARNING)
        mocked_configure_level.assert_called_once_with(logging.DEBUG if verbose else logging.INFO)
